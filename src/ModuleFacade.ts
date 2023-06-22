/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * © Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


import Spider, { AuthorData, VulnerabilityData } from "./modules/searchSECO-spider/src/Spider";
import Crawler, { CrawlData, ProjectMetadata } from "./modules/searchSECO-crawler/src/Crawler";
import Parser from "./modules/searchSECO-parser/src/Parser";
import { Flags } from "./Input";
import Logger, { Verbosity } from "./modules/searchSECO-logger/src/Logger";
import HashData from "./modules/searchSECO-parser/src/HashData";
import config from './config/config'

export default class ModuleFacade {
    private _spider: Spider
    private _crawler: Crawler
    private _parser: Parser 
    private _verbosity: Verbosity
    private _filePath: string

    constructor(filePath: string, verbosity: Verbosity) {
        this._verbosity = verbosity
        this._filePath = filePath
        this.ResetState()
    }

    public ResetState() {
        this._spider = new Spider(this._verbosity)
        this._crawler = new Crawler(config.GITHUB_TOKEN)
        this._parser = new Parser(this._verbosity)
    }

    public async DownloadRepository(repo: string, flags: Flags): Promise<boolean> {
        Logger.Debug("Deleting previously downloaded project", Logger.GetCallerLocation())
        await this._spider.clearDirectory(this._filePath)
        Logger.Debug("Calling the spider to download a repository", Logger.GetCallerLocation())
        return await this._spider.downloadRepo(repo, this._filePath, flags.Branch)
    }

    public async UpdateVersion(repo: string, prevTag: string, newTag: string, prevUnchangedFiles: string[]): Promise<string[]> {
        Logger.Debug(`Calling the spider to switch from ${prevTag} to ${newTag}`, Logger.GetCallerLocation())
        const output = await this._spider.updateVersion(prevTag, newTag, repo, prevUnchangedFiles)
        Logger.Debug("Updating finished", Logger.GetCallerLocation())
        return output
    }

    public async SwitchVersion(repo: string, tag: string) {
        Logger.Debug(`Calling the spider to switch to version ${tag}`, Logger.GetCallerLocation())
        await this._spider.switchVersion(tag, repo)
        Logger.Debug("Switching finished", Logger.GetCallerLocation())
    }

    public async TrimFiles(lines: Map<string, number[]>, repo: string) {
        Logger.Debug("Calling the spider to trim files", Logger.GetCallerLocation())
        await this._spider.trimFiles(repo, lines)
        Logger.Debug("Trimming finished", Logger.GetCallerLocation())
    }

    public async GetAuthors(repo: string, files: string[]): Promise<AuthorData> {
        Logger.Debug("Calling the spider to download author data", Logger.GetCallerLocation())
        let authorData: AuthorData = new Map()
        try {
            authorData = await this._spider.downloadAuthor(repo, files)
        }
        catch (e) {
            Logger.Warning(`Error getting authors: ${e}`, Logger.GetCallerLocation())
        }
        finally {
            Logger.Debug("Author download finished", Logger.GetCallerLocation())
        }
        return authorData
    }

    public async GetCurrentVersion(repo: string) {
        Logger.Debug("Calling the spider to get the commit hash", Logger.GetCallerLocation())
        return await this._spider.getCommitHash(repo, "HEAD")
    }

    public async GetRepositoryTags(repo: string) {
        Logger.Debug("Calling the spider to get the tags of previous versions", Logger.GetCallerLocation())
        return await this._spider.getTags(repo)
    }

    public async GetVersionTime(repo: string, version: string) {
        Logger.Debug("Calling the spider to get the version time", Logger.GetCallerLocation())
        return await this._spider.getVersionTime(repo, version)
    }

    public async ParseRepository(repo: string): Promise<[string[], HashData[]]> {
        Logger.Debug("Calling the parser to parse a repository", Logger.GetCallerLocation())
        const { filenames, result } = await this._parser.ParseFiles(repo)
        Logger.Debug("Parsing finished", Logger.GetCallerLocation())
        return [filenames, result]
    }

    public async GetProjectMetadata(url: string): Promise<ProjectMetadata> {
        Logger.Debug("Calling the crawer to get project metadata", Logger.GetCallerLocation())
        const metadata = this._crawler.getProjectMetadata(url)
        Logger.Debug("Project metadata succesfully fetched", Logger.GetCallerLocation())
        return metadata
    }

    public async CrawlRepositories(): Promise<CrawlData> {
        Logger.Debug("Calling the crawer to crawl a repository", Logger.GetCallerLocation())
        const crawldata = this._crawler.crawl()
        Logger.Debug("Crawling complete", Logger.GetCallerLocation())
        return crawldata
    }

    public async GetVulnerabilityCommits(downloadPath: string): Promise<VulnerabilityData[]> {
        Logger.Debug("Calling the spider to get vulnerability commits", Logger.GetCallerLocation())
        return await this._spider.getVulns(downloadPath)
    }

}
