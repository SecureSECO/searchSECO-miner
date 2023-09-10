/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Spider, { AuthorData, VulnerabilityData } from './modules/searchSECO-spider/src/Spider';
import Crawler, { CrawlData, ProjectMetadata } from './modules/searchSECO-crawler/src/Crawler';
import Parser from './modules/searchSECO-parser/src/Parser';
import Logger, { Verbosity } from './modules/searchSECO-logger/src/Logger';
import HashData from './modules/searchSECO-parser/src/HashData';
import config from './config/config';
import { Flags } from './Input';

export default class ModuleFacade {
	private _spider: Spider;
	private _crawler: Crawler;
	private _parser: Parser;
	private _verbosity: Verbosity;
	private _filePath: string;
	private _flags: Flags;

	constructor(filePath: string, flags: Flags, verbosity: Verbosity) {
		this._verbosity = verbosity;
		this._filePath = filePath;
		this._flags = flags;
		this._spider = new Spider(config.GITHUB_TOKEN, this._verbosity);
		this._crawler = new Crawler(config.GITHUB_TOKEN);
		this._parser = new Parser(this._verbosity, flags.Threads);
	}

	/**
	 * reinitialize modules
	 */
	public ResetParserState() {
		this._parser = new Parser(this._verbosity, this._flags.Threads);
	}

	/**
	 * Uses the spider to download a repository
	 * @param url The url to download
	 * @param branch The branch to checkout
	 * @returns True when succeeded, false when failed
	 */
	public async DownloadRepository(url: string, branch: string): Promise<boolean> {
		Logger.Debug('Deleting previously downloaded project', Logger.GetCallerLocation());
		await this._spider.clearDirectory(this._filePath);
		Logger.Debug('Calling the spider to download a repository', Logger.GetCallerLocation());
		return await this._spider.downloadRepo(url, this._filePath, branch);
	}

	/**
	 * Uses the spider to update the repository to a different tag, keeping track of unchanged files
	 * @param prevTag The previous tag
	 * @param newTag The tag to switch to
	 * @param prevUnchangedFiles An initial list of unchanged files
	 * @returns A list of updated unchanged files
	 */
	public async UpdateVersion(prevTag: string, newTag: string, prevUnchangedFiles: string[]): Promise<string[]> {
		Logger.Debug(`Calling the spider to switch from ${prevTag} to ${newTag}`, Logger.GetCallerLocation(), true);
		const output = await this._spider.updateVersion(prevTag, newTag, this._filePath, prevUnchangedFiles);
		Logger.Debug('Updating finished', Logger.GetCallerLocation());
		return output;
	}

	/**
	 * Uses the spider to switch the repository to another version
	 * @param tag The tag to switch to
	 */
	public async SwitchVersion(tag: string) {
		Logger.Debug(`Calling the spider to switch to version ${tag}`, Logger.GetCallerLocation());
		await this._spider.switchVersion(tag, this._filePath);
		Logger.Debug('Switching finished', Logger.GetCallerLocation());
	}

	/**
	 * Trims files of a repo, keeping only specified ones
	 * @param filesToKeep The files to keep
	 */
	public async TrimFiles(filesToKeep: Map<string, number[]>) {
		Logger.Debug('Calling the spider to trim files', Logger.GetCallerLocation());
		await this._spider.trimFiles(this._filePath, filesToKeep);
		Logger.Debug('Trimming finished', Logger.GetCallerLocation());
	}

	/**
     * Retrieves author data from a project, only retrieving data from specified files

     * @param files A list of files to fetch the author data for
     * @returns The fetched author data
     */
	public async GetAuthors(files: string[]): Promise<AuthorData> {
		Logger.Debug('Calling the spider to download author data', Logger.GetCallerLocation());
		let authorData: AuthorData = new Map();
		try {
			authorData = await this._spider.downloadAuthor(this._filePath, files);
		} catch (e) {
			Logger.Warning(`Error getting authors: ${e}`, Logger.GetCallerLocation());
		} finally {
			Logger.Debug('Author download finished', Logger.GetCallerLocation());
		}
		return authorData;
	}

	/**
	 * Gets the current commit hash from a repository
	 * @returns The commit hash
	 */
	public async GetCurrentVersion(): Promise<string> {
		Logger.Debug('Calling the spider to get the commit hash', Logger.GetCallerLocation());
		return await this._spider.getCommitHash(this._filePath, 'HEAD');
	}

	/**
	 * Gets a list of all repository tags
	 * @returns A list of tags with associated data
	 */
	public async GetRepositoryTags(): Promise<[string, number, string][]> {
		Logger.Debug('Calling the spider to get the tags of previous versions', Logger.GetCallerLocation());
		return await this._spider.getTags(this._filePath);
	}

	/**
	 * Gets the time string from a version of a repository
	 * @param version The commit version
	 * @returns The version time string
	 */
	public async GetVersionTime(version: string): Promise<string> {
		Logger.Debug('Calling the spider to get the version time', Logger.GetCallerLocation());
		return await this._spider.getVersionTime(this._filePath, version);
	}

	/**
	 * Uses the parser to parse a repository
	 * @returns A list of filenames and a HashData list
	 */
	public async ParseRepository(): Promise<[string[], HashData[]]> {
		Logger.Debug('Calling the parser to parse a repository', Logger.GetCallerLocation());
		const { filenames, result } = await this._parser.ParseFiles(this._filePath);
		Logger.Debug('Parsing finished', Logger.GetCallerLocation());
		return [filenames, result];
	}

	/**
	 * Retrieves project metadata
	 * @param url The url to fetch the project data from
	 * @returns The project data of the project
	 */
	public async GetProjectMetadata(url: string): Promise<ProjectMetadata> {
		try {
			Logger.Debug('Calling the crawer to get project metadata', Logger.GetCallerLocation());
			const metadata = await this._crawler.getProjectMetadata(url);
			Logger.Debug('Project metadata succesfully fetched', Logger.GetCallerLocation());
			return metadata;
		} catch (err) {
			Logger.Error(`Error getting metadata of ${url}: ${err}`, Logger.GetCallerLocation())
			return undefined
		}
	}

	/**
	 * Calls the crawler to crawl github
	 * @returns Crawl data of the crawled repos
	 */
	public async CrawlRepositories(): Promise<CrawlData> {
		Logger.Debug('Calling the crawer to crawl a repository', Logger.GetCallerLocation());
		const crawldata = this._crawler.crawl();
		Logger.Debug('Crawling complete', Logger.GetCallerLocation());
		return crawldata;
	}

	public async GetVulnerabilityCommits(): Promise<VulnerabilityData[]> {
		Logger.Debug('Calling the spider to get vulnerability commits', Logger.GetCallerLocation());
		return await this._spider.getVulns(this._filePath);
	}
}
