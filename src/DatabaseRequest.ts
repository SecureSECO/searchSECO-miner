import { TCPClient } from "./modules/searchSECO-databaseAPI/src/Client";
import { CrawlData, ProjectMetadata } from './modules/searchSECO-crawler/src/Crawler'
import config from './config/config'
import { AuthorData } from "./modules/searchSECO-spider/src/Spider";
import HashData from "./modules/searchSECO-parser/src/HashData";
import Logger from "./modules/searchSECO-logger/src/Logger";
import { RequestType } from "./modules/searchSECO-databaseAPI/src/Request";
import Error, { ErrorCode } from "./Error";
import { TCPResponse } from "./modules/searchSECO-databaseAPI/src/Response";
import cassandra from 'cassandra-driver'

function serializeData(
    data: HashData[],
    header: string,
    authors: AuthorData,
    prevCommitTime: string,
    unchangedFiles: string[]
): string[] {
    const transformedHashList = transformHashList(data)
    const authorSendData = getAuthors(transformedHashList, authors)
    return [
        header, 
        prevCommitTime, 
        unchangedFiles.join('?').replace(/\\/g, '/').replace(/.\//g, ''), 
        ...hashDataToString(data, authorSendData)
    ]
}

function transformHashList(data: HashData[]): Map<string, HashData[]>{
    const output = new Map<string, HashData[]>()
    data.forEach(hash => {
        if (!hash)
            return

        if (!output.has(hash.FileName))
            output.set(hash.FileName, [])
        
        if (output.get(hash.FileName))
            output.get(hash.FileName).push(hash)

        if (output.get(hash.FileName).length > 1 &&
            output.get(hash.FileName)[output.get(hash.FileName).length - 1].LineNumber <
            output.get(hash.FileName)[output.get(hash.FileName).length - 2].LineNumber
        ) {
            const j = output.get(hash.FileName).length - 1
            const temp = JSON.parse(JSON.stringify(output.get(hash.FileName)[j]))
            output.get(hash.FileName)[j] = JSON.parse(JSON.stringify(output.get(hash.FileName)[j-1]))
            output.get(hash.FileName)[j-1] = temp
        }
    })
    return output
}

function getAuthors(hashes: Map<string, HashData[]>, rawData: AuthorData): Map<HashData, string[]> {
    const output = new Map<HashData, string[]>()

    rawData.forEach((_, key) => {
        let currentEnd = -1, hashesIndex = -1, authorIndex = 0
        let dupes: Map<string, number>

        const h = hashes.get(key) || []
        const raw = rawData.get(key) || []

        while (h.length > 0 && raw.length > 0 && (hashesIndex < h.length || authorIndex < raw.length)) {
            if (authorIndex == raw.length || (raw[authorIndex] && currentEnd < raw[authorIndex].line)) {
                hashesIndex++
                if (hashesIndex >= h.length)
                    break
                if (authorIndex > 0)
                    authorIndex--
                currentEnd = h[hashesIndex].LineNumberEnd
                dupes = new Map<string, number>()
            }
            if (h[hashesIndex] && raw[authorIndex] && h[hashesIndex].LineNumber <=
                raw[authorIndex].line + raw[authorIndex].numLines) 
            {
                const cd = raw[authorIndex]
                const author = cd.commit.author
                const mail = cd.commit.authorMail
                const toAdd = `?${author.replace('?','')}?${mail.replace('?','')}`
                if (!dupes.get(toAdd) || dupes.get(toAdd) == 0) {
                    if (!output.has(h[hashesIndex]))
                        output.set(h[hashesIndex], [])
                    output.get(h[hashesIndex]).push(toAdd)
                    dupes.set(toAdd, 1)
                }
            }
            authorIndex++
        }
    })
    return output
}

const PARSER_VERSION = 1
function generateHeaderFromMetadata(metadata: ProjectMetadata) {
    const arr = Object.keys(metadata).filter(key => key !== "defaultBranch").map(key => {
        return metadata[key as keyof ProjectMetadata] || ''
    })
    arr.push(PARSER_VERSION)
    return arr.join('?')
}

function hashDataToString(hashData: HashData[], authors: Map<HashData, string[]>): string[] {    
    return hashData.map(item => {

        const authorArray = authors.get(item) || []

        return [
            item.Hash,
            item.FunctionName || '-',
            item.FileName.replace(/\\/g, '/').replace('./', ''),
            item.LineNumber,
            `${authorArray.length}${authorArray.join('')}`.replace(/&lt;/g, '<').replace(/&gt;/g, '>'),
            `${item.VulnCode || ''}`
        ].filter(s => s !== '').join('?')
    })
}

function serializeCrawlData(urls: CrawlData, id: string): string[] {
    const result: string[] = []

    result.push(`${urls.finalProjectId}?${id}`)

    const langs = Object.keys(urls.languages).map(lang => `${lang}?${urls.languages[lang]}`
    ).join('?')

    result.push(langs)
    
    urls.URLImportanceList.forEach(({ url, importance, finalProjectId }) => {
        result.push(`${url}?${importance}?${finalProjectId}`)
        
    })

    return result
}

export enum FinishReason {
    SUCCESS,
	UNKNOWN,
	ALREADY_KNOWN = 10,
	PROJECT_DOWNLOAD,
	TAG_RETRIEVAL,
	PROJECT_META,
	SPIDER_SETUP,
	HEAD_SWITCH,
	JOB_UPDATE,
	TAG_UPDATE,
	UPLOAD_HASHES,
	PARSER,
	AUTHOR_DATA,
	TIMEOUT
}

export default class DatabaseRequest {
    private static _client = new TCPClient("client", config.DB_HOST, config.DB_PORT, Logger.GetVerbosity())
    private static _minerId = ''
    private static _cassandraClient = new cassandra.Client({
        contactPoints: [ `${config.DB_HOST}:8002` ],
        localDataCenter: 'dcscience-vs317.science.uu.nl',
        authProvider: new cassandra.auth.PlainTextAuthProvider('cassandra', 'cassandra'),
        keyspace: 'rewarding'
    })

    public static SetMinerId(id: string) {
        this._minerId = id
    }

    public static async ConnectToCassandraNode() {
        await this._cassandraClient.connect()
        Logger.Debug('Successfully connected to Cassandra', Logger.GetCallerLocation())
    }

    public static async UploadHashes(
        hashes: HashData[],
        metadata: ProjectMetadata,
        authordata: AuthorData,
        prevCommitTime: string,
        unchangedFiles: string[]
    ): Promise<boolean> {
        const raw = serializeData(hashes, generateHeaderFromMetadata(metadata), authordata, prevCommitTime, unchangedFiles)
        Logger.Info(`Uploading ${hashes.length} methods to the database`, Logger.GetCallerLocation())
        const { responseCode } = await this._client.Execute(RequestType.UPLOAD, raw)
        if (responseCode == 200) 
            await this.incrementClaimableHashes(hashes.length)
        else Logger.Warning(`Skipping addition of ${hashes.length} hashes to the claimable hashcount`, Logger.GetCallerLocation())
        return responseCode === 200
    }

    public static async AddCrawledJobs(crawled: CrawlData, id: string): Promise<TCPResponse> {
        return await this._client.Execute(RequestType.UPLOAD_CRAWL_DATA, serializeCrawlData(crawled, id))
    }

    public static async GetProjectVersion(id: string, versionTime: string):Promise<number> {
        Logger.Debug(`Getting previous project`, Logger.GetCallerLocation())
        const { responseCode, response } = await this._client.Execute(RequestType.GET_PREVIOUS_PROJECT, [ `${id}?${versionTime}` ])
        if (response.length == 0 || responseCode != 200)
            return 0
        return parseInt((response[0] as { raw: string }).raw.split('\n')[0].split('?')[0]) || 0
    }

    public static async GetNextJob(): Promise<string> {
        Logger.Debug("Retrieving new job", Logger.GetCallerLocation())
        const { response } = await this._client.Execute(RequestType.GET_TOP_JOB, [])
        return (response[0] as { raw: string }).raw
    }

    public static async UpdateJob(jobID: string, jobTime: string): Promise<string> {
        const { response } = await this._client.Execute(RequestType.UPDATE_JOB, [`${jobID}?${jobTime}`])
        return (response[0] as { raw: string }).raw as string
    }

    public static async FinishJob(jobID: string, jobTime: string, code: FinishReason, message: string) {
        if (Error.Code != ErrorCode.HANDLED_ERRNO) {
            Error.Code = 0
            await this._client.Execute(RequestType.FINISH_JOB, [jobID, jobTime, code.toString(), message])
            if (Error.Code == 0) {
                Error.Code = ErrorCode.HANDLED_ERRNO
            }
        }
    }

    public static async RetrieveClaimableHashCount(): Promise<cassandra.types.Long> {
        Logger.Debug("Connecting with the database to retrieve all claimable hashes", Logger.GetCallerLocation())
        const query = "SELECT claimable_hashes FROM miners WHERE id=? AND wallet=?;"
        const result = await this._cassandraClient.execute(query, [
            cassandra.types.Uuid.fromString(this._minerId),
            config.PERSONAL_WALLET_ADDRESS
        ], { prepare: true })
        return result.rows[0]?.claimable_hashes || 0
    }

    private static async incrementClaimableHashes(amount: number) {
        Logger.Debug(`Incrementing claimable hash count by ${amount}`, Logger.GetCallerLocation())
        const currentCount = await this.RetrieveClaimableHashCount()
        const newCount = currentCount.add(cassandra.types.Long.fromNumber(amount))
        const query = "UPDATE rewarding.miners SET claimable_hashes=? WHERE id=? AND wallet=?;"
        await this._cassandraClient.execute(query, [ 
            newCount, 
            cassandra.types.Uuid.fromString(this._minerId),
            config.PERSONAL_WALLET_ADDRESS 
        ], { prepare: true })
        Logger.Debug(`Total of claimable hashes is now ${newCount.low}`, Logger.GetCallerLocation())
    }

    public static async ResetClaimableHashCount() {
        Logger.Debug("Resetting claimable hash count", Logger.GetCallerLocation())
        const query = "UPDATE rewarding.miners SET claimable_hashes=? WHERE wallet=?;"
        await this._cassandraClient.execute(query, [ 
            0, 
            config.PERSONAL_WALLET_ADDRESS 
        ], { prepare: true })
    }

    public static async AddMinerToDatabase(id: string, wallet: string): Promise<boolean> {
        const query = "INSERT INTO rewarding.miners (id, wallet, claimable_hashes, status) VALUES (?, ?, ?, ?) IF NOT EXISTS;"
        const result = await this._cassandraClient.execute(query, [ 
            cassandra.types.Uuid.fromString(id),
            wallet,
            cassandra.types.Long.fromNumber(0),
            'running'
        ], { prepare: true })
        return result.rows[0]['[applied]']
    }

    public static async SetMinerStatus(id: string, status: string) {
        const query = "UPDATE rewarding.miners SET status=? WHERE id=? AND wallet=?;"
        Logger.Debug(`Setting miner status to ${status}`, Logger.GetCallerLocation())
        await this._cassandraClient.execute(query, [ 
            status, 
            cassandra.types.Uuid.fromString(id), 
            config.PERSONAL_WALLET_ADDRESS 
        ], { prepare: true })
    }

    public static async ListMinersAssociatedWithWallet(wallet: string): Promise<{id: string, status: string}[]> {
        const query = "SELECT id, status FROM rewarding.miners WHERE wallet=? ALLOW FILTERING;"
        Logger.Debug(`List all miners associated with wallet ${wallet}`, Logger.GetCallerLocation())
        const response = await this._cassandraClient.execute(query, [
            wallet
        ])

        return response.rows.map((row) => ({ id: row.id.toString(), status: row.status.toString() }))
    }
}