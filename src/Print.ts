import HashData from "./modules/searchSECO-parser/src/HashData";
import fs, { WriteStream } from 'fs'
import { AuthorData } from "./modules/searchSECO-spider/src/Spider";
import path from 'path'
import { AuthorResponseData, MethodResponseData, ProjectResponseData } from "./modules/searchSECO-databaseAPI/src/Response";
import DatabaseRequest, { getAuthors, transformHashList } from "./DatabaseRequest";

type Method = {
	method_hash: string
	projectID: string
	startVersion: string
	startVersionHash: string
	endVersion: string
	endVersionHash: string
	method_name: string
	file: string
	lineNumber: string
	parserVersion: string
	vulnCode: string
	authorTotal: string
	authorIds: string[]
}

export class ObjectSet<T extends Object> {
    private _set: Set<string>
    constructor() {
        this._set = new Set()
    }

    public add(value: T): this {
        this._set.add(JSON.stringify(value))
        return this
    }

    public has(value: T): boolean {
        return this._set.has(JSON.stringify(value))
    }

    public forEach(callback: (value: T, index: number, array: T[]) => void) {
        const parsed: T[] = Array.from(this._set).map(x => JSON.parse(x))
        parsed.forEach(callback)
    }
}

function getLongestStringLength(array: string[]): number {
    return array.reduce((currentLongest, str) => str.length > currentLongest ? str.length : currentLongest, 0)
}

function lessThan(lhs: HashData, rhs: HashData): boolean {
    if (lhs.Hash !== rhs.Hash)
        return lhs.Hash < rhs.Hash
    if (lhs.FileName !== rhs.FileName)
        return lhs.FileName < rhs.FileName
    if (lhs.FunctionName !== rhs.FunctionName)
        return lhs.FunctionName < rhs.FunctionName
    if (lhs.LineNumber != rhs.LineNumber)
        return lhs.LineNumber < rhs.LineNumber
    return lhs.LineNumberEnd < rhs.LineNumberEnd
}

function line(str: string) { return `${str}\n` }
function tab(n: number) {
    let r = ''
    for (let i = 0; i < n; i++)
        r += '\t'
    return r
}
function encapsulate(str: string, c: string) { return `${c}${str}${c}` }
function quote(str: string) { return encapsulate(str, '\"') }
function plural(singular: string, n: number) { return n === 1 ? singular : `${singular}s` }


function parseDatabaseHashes(
    entries: Method[],
    receivedHashes: Map<string, Method[]>,
    projectMatches: Map<string, number>,
    projectVersions: ObjectSet<[string, string]>,
    authors: Map<string, number>
) {
    entries.forEach(method => {
        if (!receivedHashes.has(method.method_hash)) 
            receivedHashes.set(method.method_hash, [])
        receivedHashes.get(method.method_hash).push(method)

        for (let i = 0; i < parseInt(method.authorTotal); i++) {
            if (!/^[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$/.test(method.authorIds[i]))
                continue

            if (!authors.has(method.authorIds[i]))
                authors.set(method.authorIds[i], 0)
            authors.set(method.authorIds[i], authors.get(method.authorIds[i]) + 1)
        }

        if (!projectMatches.has(method.projectID))
            projectMatches.set(method.projectID, 0)
        projectMatches.set(method.projectID, projectMatches.get(method.projectID) + 1)

        if (method.startVersion) {
            projectVersions.add([method.projectID, method.startVersion])
            if (method.startVersion != method.endVersion)
                if (method.endVersion)
                    projectVersions.add([method.projectID, method.endVersion])
                else console.log(method)
        } else console.log(method)

    })
}

function getDatabaseAuthorAndProjectData(
    projectEntries: ProjectResponseData[],
    authorEntries: AuthorResponseData[],
    dbProjects: Map<string, ProjectResponseData>,
    authorIdToName: Map<string, AuthorResponseData>,
) {
    projectEntries.forEach(entry => {
        dbProjects.set(entry.id, entry)
    })

    authorEntries.forEach(entry => {
        authorIdToName.set(entry.uuid, entry)
    })
}

export default class MatchPrinter {
    private _stream: WriteStream
    constructor(fileName: string) {
        this._stream = fs.createWriteStream(path.join(__dirname, fileName))
    }

    public async PrintHashMatches(
        hashes: HashData[],
        databaseResponse: MethodResponseData[],
        authorData: AuthorData,
        url: string,
        projectID: number
    ) {

        const databaseMethods = databaseResponse.map(res => JSON.parse(JSON.stringify(res)) as Method)

        const receivedHashes = new Map<string, Method[]>()
        const projectMatches = new Map<string, number>()
        const projectVersions = new ObjectSet<[string, string]>()
        const dbAuthors = new Map<string, number>()
        const dbProjects = new Map<string, ProjectResponseData>()
        const authorIdToName = new Map<string, AuthorResponseData>()

        parseDatabaseHashes(databaseMethods, receivedHashes, projectMatches, projectVersions, dbAuthors)

        const [authorResponse, projectResponse] = await Promise.all([
            DatabaseRequest.GetAuthor(dbAuthors), 
            DatabaseRequest.GetProjectData(projectVersions)
        ])

        if (authorResponse.responseCode != 200 || projectResponse.responseCode != 200)
            return 

        const authorEntries = authorResponse.response as AuthorResponseData[]
        const projectEntries = projectResponse.response as ProjectResponseData[]


        getDatabaseAuthorAndProjectData(projectEntries, authorEntries, dbProjects, authorIdToName)

        const transformedList = transformHashList(hashes)
        const authors = getAuthors(transformedList, authorData)
        
        let matches = 0
        const authorCopiedForm = new Map<string, number>()
        const authorsCopied = new Map<string, number>()
        const vulnerabilities: [HashData, Method][] = []

        const hashMethods = new Map<string, HashData[]>()

        hashes.forEach(hash => {
            if (!hashMethods.has(hash.Hash))
                hashMethods.set(hash.Hash, [])
            hashMethods.get(hash.Hash).push(hash)
        })

        let matchesReport = ''
        receivedHashes.forEach((methods, method_hash) => {
            if (methods.reduce((projectMatch, currentMethod) => projectMatch + Number(currentMethod.projectID != projectID.toString()), 0)) {
                matches++
                matchesReport = this._printMatch(
                    hashMethods.get(method_hash),
                    methods,
                    authors,
                    projectID.toString(),
                    authorCopiedForm,
                    authorsCopied,
                    vulnerabilities,
                    dbProjects,
                    authorIdToName,
                    matchesReport
                )
            }
        })

        this._printAndWriteToFile(matchesReport)

        this._printSummary(
            authorCopiedForm,
            authorsCopied,
            vulnerabilities,
            matches,
            hashes.length,
            dbProjects,
            authorIdToName,
            projectMatches,
            url
        )
    }

    private _printMatch(
        hashes: HashData[],
        dbEntries: Method[],
        authors: Map<HashData, string[]>,
        projectID: string,
        authorCopiedForm: Map<string, number>,
        authorsCopied: Map<string, number>,
        vulnerabilities: [HashData, Method][],
        dbProjects: Map<string, ProjectResponseData>,
        authorIdToName: Map<string, AuthorResponseData>,
        report: string
    ): string {

        let currentReport = report

        const header = `Hash ${hashes[0].Hash}`
        currentReport += `${'-'.repeat(header.length)}\n`
        currentReport += `${header}\n`
        currentReport += `${'-'.repeat(header.length)}\n\n`

        hashes.forEach(hash => {
            currentReport += `  * Method ${hash.FunctionName} in file ${hash.FileName}, line ${hash.LineNumber}\n`
            currentReport += `    Authors of local function: \n`;
            (authors.get(hash) || []).forEach(s => {
                const formatted = s.replace(/\?/g, '\t')
                currentReport += `  ${formatted}\n`
                authorsCopied.set(s, (authorsCopied.get(s) || 0) + 1)
            })
            currentReport += '\n'
        })

        currentReport += '\nDATABASE\n'
        dbEntries.forEach(method => {
            if (method.projectID === projectID)
                return
            if (!dbProjects.has(method.projectID))
                return

            const linkFile = method.file.replace(/\\\\/g, '/')

            currentReport += `  * Method ${method.method_name} in project ${dbProjects.get(method.projectID).name} in file ${method.file}, line ${method.lineNumber}\n`
            currentReport += `    URL: ${dbProjects.get(method.projectID).url}/blob/${method.endVersionHash}/${linkFile}#L${method.lineNumber}\n`

            if (method.vulnCode) {
                currentReport += `   Method marked as vulnerable with code ${method.vulnCode} (https://nvd.nist.gov/vuln/detail/${method.vulnCode})`
                hashes.forEach(hash => {
                    vulnerabilities.push([hash, method])
                })
            }

            if (Number(method.authorTotal) > 0) {
                currentReport += `   Authors of function found in database: \n`
                method.authorIds.forEach(id => {
                    if (!authorIdToName.has(id)) return
                    authorCopiedForm.set(id, (authorCopiedForm.get(id) || 0) + 1)
                    currentReport += `   \t${authorIdToName.get(id).username}\t${authorIdToName.get(id).username}`
                })
            }
            currentReport += '\n'
        })

        return currentReport
    }

    private _printSummary(
        authorCopiedForm: Map<string, number>,
        authorsCopied: Map<string, number>,
        vulnerabilities: [HashData, Method][],
        matches: number,
        methods: number,
        dbProjects: Map<string, ProjectResponseData>,
        authorIdToName: Map<string, AuthorResponseData>,
        projectMatches: Map<string, number>,
        url: string
    ) {
        this._printAndWriteToFile(`\nSummary:`)
        this._printAndWriteToFile(`Checked project url: ${url}`)
        this._printAndWriteToFile(`Methods in checked project: ${methods}`)

        this._printAndWriteToFile(`Matches: ${matches} (${(matches * 100 / methods).toFixed(2)}%)`)

        if (vulnerabilities.length > 0) {
            this._printAndWriteToFile('\nVulnerabilities found:')
            vulnerabilities.forEach(([ hashData, method ]) => {
                this._printAndWriteToFile(
                    `Method with hash ${hashData.Hash} was found to be vulnerable in ${dbProjects.get(method.projectID).name} with code ${method.vulnCode} (https://nvd.nist.gov/vuln/detail/${method.vulnCode})`
                )

            })
        }

        this._printAndWriteToFile('\nProjects found in database: ')
        const vprojects: [number, string, string][] = []

        projectMatches.forEach((value, key) => {
            if (!dbProjects.has(key))
                return
            vprojects.push([value, dbProjects.get(key).name, dbProjects.get(key).url])
        })

        const longestProjectName = getLongestStringLength(vprojects.map(([,projectName,]) => projectName))

        vprojects.sort().reverse()
        vprojects.forEach(([ matchCount, projectName, projectURL ]) => {
            this._printAndWriteToFile(
                `\t${projectName}${' '.repeat(longestProjectName - projectName.length - matchCount.toString().length + 5)}${matchCount} (${projectURL})`
            )
        })

        const localAuthors: [number, string, string][] = []
        authorsCopied.forEach((value, key) => {
            const author = key.split('?')
            localAuthors.push([ value, author[1], author[2] ])
        })

        const remoteAuthors: [number, string, string][] = []
        authorCopiedForm.forEach((value, key) => {
            const author = authorIdToName.get(key)
            remoteAuthors.push([ value, author.username, author.email ])
        })

        const longestAuthorName = getLongestStringLength([
            ...localAuthors.map(([,authorName,]) => authorName), 
            ...remoteAuthors.map(([,authorName,]) => authorName)
        ])

        localAuthors.sort().reverse()
        remoteAuthors.sort().reverse()

        this._printAndWriteToFile('\nLocal authors present in matches:')
        localAuthors.forEach(([ matchCount, authorName, authorEmail ]) => {
            this._printAndWriteToFile(
                `\t${authorName}${' '.repeat(longestAuthorName - authorName.length - matchCount.toString().length + 5)}${matchCount} ${authorEmail}`
            )
        })

        this._printAndWriteToFile('\nAuthors present in database matches:')
        remoteAuthors.forEach(([ matchCount, authorName, authorEmail ]) => {
            this._printAndWriteToFile(
                `\t${authorName}${' '.repeat(longestAuthorName - authorName.length - matchCount.toString().length + 5)}${matchCount} ${authorEmail}`
            )
        })
        this._printAndWriteToFile('\n')
    }

    private _writeLineToFile(str: string) {
        this._stream.cork()
        this._stream.write(line(str))
        process.nextTick(() => this._stream.uncork())
    }
    private _printAndWriteToFile(str: string) {
        console.log(str)
        this._writeLineToFile(str)
    }

    public Close() {
        this._stream.close()
    }
}

