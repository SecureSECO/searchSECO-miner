
import Spider, { AuthorData, VulnerabilityData } from "./modules/searchSECO-spider/src/Spider";
import Crawler, { CrawlData, ProjectMetadata } from "./modules/searchSECO-crawler/src/Crawler";
import Parser from "./modules/searchSECO-parser/src/Parser";
import { Flags } from "./Input";
import Logger from "./modules/searchSECO-logger/src/Logger";
import path from 'path'
import HashData from "./modules/searchSECO-parser/src/HashData";
import config from './config/config'

export default class ModuleFacade {
    public static Spider: Spider = new Spider(Logger.GetVerbosity())
    public static Crawler: Crawler = new Crawler(config.GITHUB_TOKEN)
    private static _filePath = path.join(__dirname, '../.tmp')

    public static async SetFilePath(path: string) {
        this._filePath = path
    }

    public static async DownloadRepository(repo: string, flags: Flags): Promise<boolean> {
        Logger.Debug("Deleting previously downloaded project", Logger.GetCallerLocation())
        await this.Spider.clearDirectory(this._filePath)
        Logger.Debug("Calling the spider to download a repository", Logger.GetCallerLocation())
        return await this.Spider.downloadRepo(repo, this._filePath, flags.Branch)
    }

    public static async UpdateVersion(repo: string, prevTag: string, newTag: string, prevUnchangedFiles: string[]): Promise<string[]> {
        Logger.Debug(`Calling the spider to switch from ${prevTag} to ${newTag}`, Logger.GetCallerLocation())
        const output = await this.Spider.updateVersion(prevTag, newTag, repo, prevUnchangedFiles)
        Logger.Debug("Updating finished", Logger.GetCallerLocation())
        return output
    }

    public static async SwitchVersion(repo: string, tag: string) {
        Logger.Debug(`Calling the spider to switch to version ${tag}`, Logger.GetCallerLocation())
        await this.Spider.switchVersion(tag, repo)
        Logger.Debug("Switching finished", Logger.GetCallerLocation())
    }

    public static async TrimFiles(lines: Map<string, number[]>, repo: string) {
        Logger.Debug("Calling the spider to trim files", Logger.GetCallerLocation())
        await this.Spider.trimFiles(repo, lines)
        Logger.Debug("Trimming finished", Logger.GetCallerLocation())
    }

    public static async GetAuthors(repo: string): Promise<AuthorData> {
        Logger.Debug("Calling the spider to download author data", Logger.GetCallerLocation())
        let authorData: AuthorData = new Map()
        try {
            authorData = await this.Spider.downloadAuthor(repo)
        }
        catch (e) {
            Logger.Warning(`Error getting authors: ${e}`, Logger.GetCallerLocation())
        }
        finally {
            Logger.Debug("Author download finished", Logger.GetCallerLocation())
        }
        return authorData
    }

    public static async GetCurrentVersion(repo: string) {
        Logger.Debug("Calling the spider to get the commit hash", Logger.GetCallerLocation())
        return await this.Spider.getCommitHash(repo, "HEAD")
    }

    public static async GetRepositoryTags(repo: string) {
        Logger.Debug("Calling the spider to get the tags of previous versions", Logger.GetCallerLocation())
        return await this.Spider.getTags(repo)
    }

    public static async GetVersionTime(repo: string, version: string) {
        Logger.Debug("Calling the spider to get the version time", Logger.GetCallerLocation())
        return await this.Spider.getVersionTime(repo, version)
    }

    public static async ParseRepository(repo: string): Promise<HashData[]> {
        Logger.Debug("Calling the parser to parse a repository", Logger.GetCallerLocation())
        const hashes = (await Parser.ParseFiles(repo, Logger.GetVerbosity())).result
        Logger.Debug("Parsing finished", Logger.GetCallerLocation())
        return hashes
    }

    public static async GetProjectMetadata(url: string): Promise<ProjectMetadata> {
        Logger.Debug("Calling the crawler to get project metadata", Logger.GetCallerLocation())
        const metadata = this.Crawler.getProjectMetadata(url)
        Logger.Debug("Project metadata succesfully fetched", Logger.GetCallerLocation())
        return metadata
    }

    public static async CrawlRepositories(): Promise<CrawlData> {
        Logger.Debug("Calling the crawler to crawl a repository", Logger.GetCallerLocation())
        const crawldata = this.Crawler.crawl()
        Logger.Debug("Crawling complete", Logger.GetCallerLocation())
        return crawldata
    }

    public static async GetVulnerabilityCommits(downloadPath: string): Promise<VulnerabilityData[]> {
        Logger.Debug("Calling the spider to get vulnerability commits", Logger.GetCallerLocation())
        return await this.Spider.getVulns(downloadPath)
    }

}