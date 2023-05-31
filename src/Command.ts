import EnvironmentDTO from "./EnvironmentDTO";
import { Flags } from "./Input";
import HashData from "./modules/searchSECO-parser/src/HashData";
import { AuthorData } from "./modules/searchSECO-spider/src/Spider";
import ModuleFacade from "./ModuleFacade";
import path from 'path'
import Logger from "./modules/searchSECO-logger/src/Logger";
import DatabaseRequest, { FinishReason } from "./DatabaseRequest";
import { ProjectMetadata } from "./modules/searchSECO-crawler/src/Crawler";
import Error from './Error'
import { JobResponseData } from "./modules/searchSECO-databaseAPI/src/Response";

const DOWNLOAD_LOCATION = path.join(__dirname, "../.tmp")
const TAGS_COUNT = 20

export class SigInt {
    public static Stop: boolean = false
    public static IsStopped: boolean = false
    public static async StopProcess() {
        this.Stop = true
        while (!this.IsStopped)
            await new Promise(resolve => (setTimeout(resolve, 5000)))
    }
    public static ResumeProcess() {
        this.Stop = false
    }
}

export default abstract class Command {
    protected static _helpMessageText: string
    protected _flags: Flags
    protected _env: EnvironmentDTO

    constructor(flags: Flags, env: EnvironmentDTO) {
        this._flags = flags
        this._env = env
    }

    public static GetHelpMessage(): string {
        return this._helpMessageText
    }

    public abstract Execute(): Promise<void>;

    protected async parseAndBlame(tag: string, jobID: string, jobTime: string) 
        : Promise<[HashData[], AuthorData]>
    {
        const hashes = await ModuleFacade.ParseRepository(DOWNLOAD_LOCATION, this._flags)

        if (hashes.length == 0) {
            Logger.Debug("No methods found, skipping authors", Logger.GetCallerLocation())
            return [hashes, new Map() as AuthorData]
        }

        const authorData = await ModuleFacade.GetAuthors(DOWNLOAD_LOCATION)
        return [hashes, authorData]
    }

    protected async uploadProject(jobID: string, jobTime: string, startTime: number) {
        Logger.Info("Uploading project to database", Logger.GetCallerLocation())

        const metadata = await ModuleFacade.GetProjectMetadata(this._flags.MandatoryArgument, this._flags)

        if (!metadata) {
            Logger.Warning("Error getting project metadata. Moving on", Logger.GetCallerLocation())
            return
        }

        if (!this._flags.Branch || (["main", "master"].includes(this._flags.Branch) && this._flags.Branch !== metadata.defaultBranch))
            this._flags.Branch = metadata.defaultBranch
        Logger.Debug(`Default branch is ${metadata.defaultBranch}`, Logger.GetCallerLocation())
        
        let startingTime = await DatabaseRequest.GetProjectVersion(metadata.id.toString(), metadata.versionTime)
        if (parseInt(metadata.versionTime) <= startingTime) {
            Logger.Info("Most recent version already in database", Logger.GetCallerLocation())
            Logger.Warning("This needs to be logged to a file!", Logger.GetCallerLocation())
            return
        }

        await ModuleFacade.DownloadRepository(this._flags.MandatoryArgument, this._flags)        
        metadata.versionHash = await ModuleFacade.GetCurrentVersion(DOWNLOAD_LOCATION)

        const vulnCommits = await ModuleFacade.GetVulnerabilityCommits(DOWNLOAD_LOCATION)
        Logger.Info(`${vulnCommits.length} vulnerabilities found in project`, Logger.GetCallerLocation())
        Logger.Warning("This needs to be logged to a file!", Logger.GetCallerLocation())

        vulnCommits.forEach(async commit => {
            Logger.Debug(`Uploading vulnerability: ${commit.vulnerability}`, Logger.GetCallerLocation())
            jobTime = await DatabaseRequest.UpdateJob(jobID, jobTime)
            startTime = Date.now()
            await this.uploadPartialProject(commit.commit, commit.lines, commit.vulnerability, metadata)
        })

        await ModuleFacade.SwitchVersion(DOWNLOAD_LOCATION, this._flags.Branch)
        let tags = await ModuleFacade.GetRepositoryTags(DOWNLOAD_LOCATION)
        let tagc = tags.length

        Logger.Info(`Project has ${tagc} tag(s)`, Logger.GetCallerLocation())
        Logger.Warning("This needs to be logged to a file!", Logger.GetCallerLocation())

        if (tagc > TAGS_COUNT) {
            const newTags: [string, number, string][] = []
            const fraction = (tagc - 1) / (TAGS_COUNT - 1)
            for (let i = 0; i < TAGS_COUNT; i++)
                newTags[i] = tags[fraction * i]
            tags = JSON.parse(JSON.stringify(newTags))
            tagc = TAGS_COUNT
        }

        if (parseInt(metadata.versionTime) > startingTime && tagc == 0) {
            await this.parseLatest(metadata, startingTime.toString(), jobID, jobTime)
        }
        else if (tagc != 0) {
            if (tags[tagc-1][1] <= startingTime) {
                Logger.Info("Latest tag of project already in database", Logger.GetCallerLocation())
                Logger.Warning("This needs to be logged to a file!", Logger.GetCallerLocation())
                return
            }
            await this.loopThroughTags(tags, metadata, startingTime, jobID, jobTime, startTime)
        }
    }

    protected async uploadPartialProject(version: string, lines: Map<string, number[]>, vulnCode: string, metadata: ProjectMetadata) {
        if (!metadata.id) {
            const newMetadata = await ModuleFacade.GetProjectMetadata(this._flags.MandatoryArgument, this._flags)
            if (!this._flags.Branch)
                this._flags.Branch = newMetadata.defaultBranch
        }

        // await ModuleFacade.DownloadRepository(this._flags.MandatoryArgument, this._flags)
        await Promise.all([
            ModuleFacade.SwitchVersion(version, DOWNLOAD_LOCATION),
            ModuleFacade.TrimFiles(lines, DOWNLOAD_LOCATION)
        ])

        let hashes = await ModuleFacade.ParseRepository(DOWNLOAD_LOCATION, this._flags)
        hashes = this.trimHashes(hashes, lines)
        if (hashes.length == 0) {
            Logger.Debug("No methods present, skipping authors", Logger.GetCallerLocation())
            return
        }
        hashes.forEach(hash => {
            hash.VulnCode = vulnCode
        })

        const authorData = await ModuleFacade.GetAuthors(DOWNLOAD_LOCATION)
        metadata.versionTime = await ModuleFacade.GetVersionTime(DOWNLOAD_LOCATION, version)
        metadata.versionHash = version
        await DatabaseRequest.UploadHashes(hashes, metadata, authorData, "", [])
    }

    protected async checkProject() {
        const url = this._flags.MandatoryArgument
        // TODO: implement correct type
        const metadata: any = ModuleFacade.GetProjectMetadata(url, this._flags)
        if (!metadata) {
            Logger.Warning("Error getting project metadata, moving on to next job", Logger.GetCallerLocation())
            return
        }

        if (!this._flags.Branch)
            this._flags.Branch = metadata.defaultBranch
        
        await ModuleFacade.DownloadRepository(url, this._flags)
        if (this._flags.ProjectCommit)
            ModuleFacade.SwitchVersion(this._flags.ProjectCommit, DOWNLOAD_LOCATION)
        
        const [ hashes, authorData ] = await this.parseAndBlame("HEAD", "0", "")
        
    }

    private async parseLatest(metadata: ProjectMetadata, startingTime: string, jobID: string, jobTime: string) {
        Logger.Debug("No tags found, just looking at HEAD", Logger.GetCallerLocation())
        const [hashes, authorData] = await this.parseAndBlame("HEAD", jobID, jobTime)
        if (hashes.length == 0)
            return
        Logger.Debug("Uploading hashes", Logger.GetCallerLocation())
        await DatabaseRequest.UploadHashes(hashes, metadata, authorData, "", [])
    }

    private async loopThroughTags(tags: [string, number, string][], metadata: ProjectMetadata, startingTime: number, jobID: string, jobTime: string, startTime: number) {
        let i = 0
        while (tags[i][1] <= startingTime)
            i++
        
        let prevTag = ""
        let prevVersionTime = ""
        let prevUnchangedFiles: string[] = []

        if (i > 0) {
            prevTag = tags[i-1][0]
            prevVersionTime = tags[i-1][1].toString()
        }

        for (; i < tags.length; i++) {
            const currTag = tags[i][0]
            const versionTime = tags[i][1]
            const versionHash = tags[i][2]

            metadata.versionTime = versionTime.toString()
            metadata.versionHash = versionHash

            Logger.Info(`Processing tag: ${currTag} (${i+1}/${tags.length})`, Logger.GetCallerLocation())
            Logger.Warning("This needs to be logged to a file!", Logger.GetCallerLocation())
            Logger.Debug(`Comparing tags: ${prevTag} and ${currTag}.`, Logger.GetCallerLocation())

            await DatabaseRequest.UpdateJob(jobID, jobTime)

            startTime = Date.now()
            await this.downloadTagged(prevTag, currTag, metadata, prevVersionTime, prevUnchangedFiles, jobID, jobTime)
        }
    }

    private async downloadTagged(prevTag: string, currTag: string, metadata: ProjectMetadata, prevVersionTime: string, prevUnchangedFiles: string[], jobID: string, jobTime: string) {
        const [unchangedFiles, [hashes, authorData]] = await Promise.all([
            ModuleFacade.UpdateVersion(DOWNLOAD_LOCATION, prevTag, currTag, prevUnchangedFiles), 
            this.parseAndBlame(currTag, jobID, jobTime)
        ])
        await DatabaseRequest.UploadHashes(hashes, metadata, authorData, prevVersionTime, unchangedFiles)
        prevUnchangedFiles = unchangedFiles
    }

    private trimHashes(hashes: HashData[], lines: Map<string, number[]>) {
        const result: HashData[] = []
        hashes.forEach(hash => {
            lines.get(hash.FileName).forEach(line => {
                if (hash.LineNumber <= line && line <= hash.LineNumberEnd) {
                    result.push(hash)
                    return
                }
            })
        })
        return result
    }

}

export class StartCommand extends Command {
    protected static _helpMessageText: string = "Start the miner"
    constructor(flags: Flags, env: EnvironmentDTO) {
        super(flags, env)
    }

    public async Execute(): Promise<void> {
        this._flags.Branch = ""
        Logger.Info("Starting miner...", Logger.GetCallerLocation())

        while (!SigInt.Stop) {
            const job = await DatabaseRequest.GetNextJob()
            const splitted = job.split('?')
            switch (splitted[0]) {
                case "Spider":
                    Logger.Info(`New Job: Download and parse ${splitted[2]}`, Logger.GetCallerLocation())
                    const startTime = Date.now()
                    await this.processVersion(splitted, startTime)
                    break;
                
                case "Crawl":
                    Logger.Info("New Job: Crawl for more URLs", Logger.GetCallerLocation())
                    await this.handleCrawlRequest(splitted)
                    break;
                
                case "NoJob":
                    Logger.Info("Waiting for a new job", Logger.GetCallerLocation())
                    await new Promise(resolve => setTimeout(resolve, 5000))
                    break;

                default: 
                    Logger.Warning("Unknown job type", Logger.GetCallerLocation())
                    break;
            }
        }

        SigInt.IsStopped = true
    }

    public HandleTimeout() {

    }

    private async handleCrawlRequest(splitted: string[]) {
        const crawled = await ModuleFacade.CrawlRepositories(parseInt(splitted[1]), this._flags)
        await DatabaseRequest.AddCrawledJobs(crawled, splitted[2])
    }

    private async processVersion(splitted: string[], startTime: number) {
        if (splitted.length < 5 || !splitted[2]) {
            Logger.Warning("Unexpected job data received from database", Logger.GetCallerLocation())
            return
        }
        this._flags.MandatoryArgument = splitted[2]
        await this.uploadProject(splitted[1], splitted[3], startTime)
    }

    private readCommandLine() {

    }
}

