/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Flags } from './Input';
import HashData from './modules/searchSECO-parser/src/HashData';
import { AuthorData } from './modules/searchSECO-spider/src/Spider';
import ModuleFacade from './ModuleFacade';
import path from 'path';
import Logger, { Verbosity } from './modules/searchSECO-logger/src/Logger';
import { ProjectMetadata } from './modules/searchSECO-crawler/src/Crawler';
import MatchPrinter from './Print';
import config from './config/config';
import { CheckResponse, CrawlTask, JobId, JsonRequest, ProjectInfoResponseItem, ProjectWithVersion, SpiderTask } from './JsonRequest';

/**
 * Makes a designated repo download location for the current miner.
 * @param minerId The ID of the current miner
 * @returns a path string representing the repo download location for the current miner.
 */

const isPackage = (process as any).pkg ? true : false
const TEMP_FOLDER = isPackage ? './.tmp' : '../.tmp'
const WORKING_DIR = isPackage ? path.dirname(process.argv[0]) : __dirname;
const DOWNLOAD_LOCATION = (minerId: string) => path.resolve(WORKING_DIR, `${TEMP_FOLDER}/${minerId}`);

/**
 * Static class storing SIGINT signals.
 * This is used to stop the current process when a SIGINT is fired.
 */
export class SigInt {
	public static Stop = false;
	public static IsStopped = false;
	/**
	 * Signals that the process needs to be stopped.
	 * Waits until the process signals that it's actually stopped.
	 * @param minerId The miner ID associated with the current process.
	 */
	public static async StopProcess(minerId: string) {
		this.Stop = true;
		while (!this.IsStopped) await new Promise((resolve) => setTimeout(resolve, 1000));
		if (this.Stop) await this.stop(minerId);
	}
	/**
	 * Resumes the process if it was gracefully stopped with the SigInt.StopProcess() function
	 */
	public static ResumeProcess() {
		this.Stop = false;
	}
	/**
	 * Gracefully stops the process immediately.
	 * @param minerId The miner ID associated with the current process
	 */
	public static async StopProcessImmediately(minerId: string) {
		await this.stop(minerId);
	}

	private static async stop(minerId: string) {
		process.exit(0);
	}
}

/**
 * The base Command class. This class holds most of the functionalities for modifying repositories
 */
export default abstract class Command {
	protected static _helpMessageText: string;
	protected _flags: Flags;
	protected _minerId: string;

	protected _moduleFacade: ModuleFacade;

	constructor(minerId: string, flags: Flags) {
		this._flags = flags;
		this._minerId = minerId;

		this._moduleFacade = new ModuleFacade(DOWNLOAD_LOCATION(this._minerId), flags, Logger.GetVerbosity());
	}

	/**
	 * Gets the help message associated with the current command
	 * @returns The help message associated with the current command
	 */
	public static GetHelpMessage(): string {
		return this._helpMessageText;
	}

	/**
	 * Executes the command.
	 */
	public abstract Execute(verbosity: Verbosity): Promise<void>;

	/**
	 * Parses a project and retrieves author data.
	 * AuthorData is a map from filenames to CodeBlocks
	 * @returns a tuple containing a HashData array and an AuthorData object
	 */
	protected async parseAndBlame(): Promise<[HashData[], AuthorData]> {
		const [filenames, methods] = await this._moduleFacade.ParseRepository();
		if (methods.length == 0) {
			Logger.Debug('No methods found, skipping authors', Logger.GetCallerLocation());
			return [methods, new Map() as AuthorData];
		}
		// Select the files where we found a method
		const filteredFileNames: string[] = [];
		methods.forEach((hash) => {
			const idx = filenames.findIndex((file) => file === hash.FileName);
			if (idx < 0) return;
			filteredFileNames.push(filenames[idx]);
			filenames.splice(idx, 1);
		});
		const authorData = await this._moduleFacade.GetAuthors(filteredFileNames);
		return [methods, authorData];
	}


	static add_if_new(pid: number, version: number, pv_map: Map<number, number[]>) {
		let pid_list = pv_map.get(pid);
		if (!pid_list) {
			pv_map.set(pid, [version]);
		} else if (!pid_list.includes(version)) {
			pid_list.push(version);
		}

	}

	static get_project_versions(methods: CheckResponse[]): ProjectWithVersion[] {
		let map: Map<number, number[]> = new Map();
		methods.forEach(m => {
			if (m.sv_time) {
				this.add_if_new(m.pid, m.sv_time, map);
			}
			if (m.ev_time) {
				this.add_if_new(m.pid, m.ev_time, map);
			}
		})
		let result: ProjectWithVersion[] = [];
		map.forEach((vs, k) => {
			vs.forEach((v) => result.push({ project_id: k, version: v }));
		});
		return result;
	}

	static get_project_authors(methods: CheckResponse[]): Set<string> {
		let authors: Set<string> = new Set();
		methods.forEach(m => {
			m.authors.forEach(a => authors.add(a))
		})
		return authors;
	}

	static order_project_info(pi_items: ProjectInfoResponseItem[]): Map<number, ProjectInfoResponseItem[]> {
		let result = new Map<number, ProjectInfoResponseItem[]>();
		pi_items.forEach((pi) => {
			let pi_list = result.get(pi.pid);
			if (!pi_list) {
				result.set(pi.pid, [pi]);
			} else {
				pi_list.push(pi);
			}
		})
		return result;
	}

	protected async checkProject(): Promise<boolean> {
		const url = this._flags.MandatoryArgument;
		Logger.Info(`Checking ${url} against the SearchSECO database`, Logger.GetCallerLocation());

		const metadata = await this._moduleFacade.GetProjectMetadata(url);
		if (!metadata) return false;

		if (!this._flags.Branch)
			this._flags.Branch = metadata.defaultBranch;

		await this._moduleFacade.DownloadRepository(url, this._flags.Branch);

		if (this._flags.ProjectCommit !== '')
			await this._moduleFacade.SwitchVersion(this._flags.ProjectCommit);

		const [projectMethods, projectBlaming] = await this.parseAndBlame();
		const projectHashes = Array.from(new Set<string>(projectMethods.map((hash) => hash.Hash)));
		const checkResponse: CheckResponse[] = await JsonRequest.FindMatches(projectHashes);
		const dbProjectIds = Command.get_project_versions(checkResponse);
		const dbProjectInfo = Command.order_project_info(await JsonRequest.GetProjectData(dbProjectIds));
		const authorIds = Command.get_project_authors(checkResponse);
		const dbAuthorInfo = await JsonRequest.GetAuthorData(authorIds.values());


		const printer = new MatchPrinter();
		await printer.PrintHashMatches(url, metadata.id, projectMethods, projectBlaming, checkResponse, dbProjectInfo, dbAuthorInfo);
		printer.Close();
		await this._moduleFacade.ClearRepository();

		return true
	}

	/**
	 * Processes a project and uploads it to the database.
	 * @param jobID The current job ID
	 * @param jobTime The time the job has been uploaded
	 * @param startTime The time the job started
	 */
	protected async uploadProject(jobID: string, jobTime: number, startTime: number): Promise<void> {
		Logger.Info('Processing and uploading project to database', Logger.GetCallerLocation());
		let job = null;
		if (jobID != '') {
			job = { "jid": jobID, "time": jobTime };
		}

		const metadata = await this._moduleFacade.GetProjectMetadata(this._flags.MandatoryArgument);
		if (!metadata) return;

		// Set default branch
		if (
			!this._flags.Branch ||
			(['main', 'master'].includes(this._flags.Branch) && this._flags.Branch !== metadata.defaultBranch)
		)
			this._flags.Branch = metadata.defaultBranch;
		Logger.Debug(`Default branch is ${this._flags.Branch}`, Logger.GetCallerLocation());

		const startingTime = await JsonRequest.LastVersion(metadata.id);
		if (startingTime > 0 && metadata.versionTime <= startingTime) {
			Logger.Info('Most recent version already in database', Logger.GetCallerLocation());
			return;
		}

		const success = await this._moduleFacade.DownloadRepository(this._flags.MandatoryArgument, this._flags.Branch);
		if (!success)
			return;
		metadata.versionHash = await this._moduleFacade.GetCurrentVersion();

		const vulnCommits = await this._moduleFacade.GetVulnerabilityCommits();
		Logger.Info(`${vulnCommits.length} vulnerabilities found in project`, Logger.GetCallerLocation(), true);

		for (const commit of vulnCommits) {
			Logger.Info(`Uploading vulnerability: ${commit.vulnerability}`, Logger.GetCallerLocation(), true);
			Logger.Warning(`Uploading currently disabled (not implemented)`, Logger.GetCallerLocation(), true);

			//if (config.COMMAND === 'start') {
			//	jobTime = await DatabaseRequest.UpdateJob(jobID, jobTime);
			//	startTime = Date.now();
			//}

			//await this.uploadPartialProject(commit.commit, commit.lines, commit.vulnerability, metadata);
		}

		if (metadata.defaultBranch !== this._flags.Branch)
			await this._moduleFacade.SwitchVersion(this._flags.Branch);
		//const tags = await this._moduleFacade.GetRepositoryTags();
		//const tagc = tags.length;

		await this.parseLatest(metadata, job);
		/*
		if (metadata.versionTime > startingTime && tagc == 0) {
			await this.parseLatest(metadata);
		} else if (tagc != 0) {
			if (tags[tagc - 1][1] <= startingTime) {
				Logger.Info('Latest tag of project already in database', Logger.GetCallerLocation());
				return;
			}
			await this.loopThroughTags(tags, metadata, startingTime, jobID, jobTime);
		}
		*/
		await this._moduleFacade.ClearRepository();
	}

	/**
	 * Uploads a single version of a project
	 * @param version The version to upload
	 * @param filesToKeep The files to keep after trim
	 * @param vulnCode The vulnerability code of the project version
	 * @param metadata The project metadata
	 */
	protected async uploadPartialProject(
		version: string,
		filesToKeep: Map<string, number[]>,
		vulnCode: string,
		metadata: ProjectMetadata
	) {
		if (!metadata.id) {
			const newMetadata = await this._moduleFacade.GetProjectMetadata(this._flags.MandatoryArgument);
			if (!this._flags.Branch) this._flags.Branch = newMetadata.defaultBranch;
		}

		await this._moduleFacade.SwitchVersion(version), await this._moduleFacade.TrimFiles(filesToKeep);

		const [filenames, hashes] = await this._moduleFacade.ParseRepository();
		const trimmedHashes = this.trimHashes(hashes, filesToKeep);
		if (trimmedHashes.length == 0) {
			Logger.Debug('No methods present after trim, skipping authors', Logger.GetCallerLocation());
			return;
		}
		trimmedHashes.forEach((hash) => {
			hash.VulnCode = vulnCode;
		});
		const filteredFileNames: string[] = [];
		trimmedHashes.forEach((hash) => {
			filteredFileNames.push(
				filenames[
				filenames.findIndex((file) => {
					file.includes(hash.FileName);
				})
				]
			);
		});
		const authorData = await this._moduleFacade.GetAuthors(filteredFileNames);
		metadata.versionTime = await this._moduleFacade.GetVersionTime(version);
		metadata.versionHash = version;
		await JsonRequest.UploadHashes(trimmedHashes, metadata, authorData, -1, [], null);
	}

	/**
	 * Parse the latest version of a project
	 * @param metadata The metadata of the project
	 */
	private async parseLatest(metadata: ProjectMetadata, job: null | JobId) {
		Logger.Debug('No tags found, just looking at HEAD', Logger.GetCallerLocation());
		const [hashes, authorData] = await this.parseAndBlame();
		if (hashes.length == 0) return;
		Logger.Debug('Uploading hashes', Logger.GetCallerLocation());
		await JsonRequest.UploadHashes(hashes, metadata, authorData, -1, [], job);
	}

	/**
	 * Loops through tags and uploads each version
	 * @param tags The tags to loop through
	 * @param metadata The project metadata
	 * @param startingTime The time when the job has started
	 * @param jobID the job id
	 * @param jobTime the current time of the job
	 */
	private async loopThroughTags(
		tags: [string, number, string][],
		metadata: ProjectMetadata,
		startingTime: number,
		jobID: string,
		jobTime: number
	) {
		let i = 0;
		while (tags[i][1] <= startingTime) i++;

		let prevTag = '';
		let prevVersionTime = -1;
		const prevUnchangedFiles: string[] = [];

		if (i > 0) {
			prevTag = tags[i - 1][0];
			prevVersionTime = tags[i - 1][1];
		}

		for (; i < tags.length; i++) {
			const currTag = tags[i][0];
			const versionTime = tags[i][1];
			const versionHash = tags[i][2];

			metadata.versionTime = versionTime;
			metadata.versionHash = versionHash;

			Logger.Info(`Processing tag: ${currTag} (${i + 1}/${tags.length})`, Logger.GetCallerLocation());
			Logger.Debug(`Comparing tags: ${prevTag} and ${currTag}.`, Logger.GetCallerLocation());

			//if (config.COMMAND === 'start') jobTime = await DatabaseRequest.UpdateJob(jobID, jobTime);

			const success = await this.downloadTagged(prevTag, currTag, metadata, prevVersionTime, prevUnchangedFiles);
			if (!success) break;

			prevTag = currTag;
			prevVersionTime = versionTime;
		}
	}

	/**
	 * Switches the project to another version
	 * @param prevTag The previous tag of the project
	 * @param currTag The tag to switch to
	 * @param metadata the project metadata
	 * @param prevVersionTime The time of the previous version
	 * @param prevUnchangedFiles All unchanged files of the previous version
	 * @returns True when the switching has finished successfully
	 */
	private async downloadTagged(
		prevTag: string,
		currTag: string,
		metadata: ProjectMetadata,
		prevVersionTime: number,
		prevUnchangedFiles: string[]
	): Promise<boolean> {
		const unchangedFiles = await this._moduleFacade.UpdateVersion(prevTag, currTag, prevUnchangedFiles);
		const [hashes, authorData] = await this.parseAndBlame();
		const success = await JsonRequest.UploadHashes(hashes, metadata, authorData, prevVersionTime, unchangedFiles, null);
		prevUnchangedFiles = unchangedFiles;
		return success;
	}

	private trimHashes(hashes: HashData[], lines: Map<string, number[]>) {
		const result: HashData[] = [];
		hashes.forEach((hash) => {
			(lines.get(hash.FileName) || []).forEach((line) => {
				if (hash.LineNumber <= line && line <= hash.LineNumberEnd) {
					result.push(hash);
					return;
				}
			});
		});
		return result;
	}
}

export class StartCommand extends Command {
	protected static _helpMessageText = 'Start the miner';
	constructor(minerId: string, flags: Flags) {
		super(minerId, flags);
	}

	public async Execute(verbosity: Verbosity): Promise<void> {
		Logger.Debug('Starting loop', Logger.GetCallerLocation());
		while (!SigInt.Stop) {
			this._moduleFacade.ResetParserState();

			this._flags.Branch = '';
			const task = await JsonRequest.GetTask();
			if (task == "No") {
				Logger.Debug('Waiting for a new job', Logger.GetCallerLocation());
				await new Promise((resolve) => setTimeout(resolve, 5000));
			} else if ("Spider" in task) {
				let spiderTask = task.Spider;
				Logger.Debug(`New Job: Download and parse ${spiderTask.url}`, Logger.GetCallerLocation());
				const startTime = Date.now();
				await this.processVersion(spiderTask, startTime);
			} else {
				let crawlTask = task.Crawl;
				Logger.Debug('New Job: Crawl for more URLs', Logger.GetCallerLocation());
				await this.handleCrawlRequest(crawlTask);
			}
		}

		SigInt.IsStopped = true;
	}

	public HandleTimeout() {
		/* empty */
	}

	private async handleCrawlRequest(task: CrawlTask) {
		const crawled = await this._moduleFacade.CrawlRepositories();
		Logger.Info('Received data from crawler', Logger.GetCallerLocation());
		await JsonRequest.AddCrawledJobs(crawled, task)
		Logger.Info('Sent crawl data to DB.', Logger.GetCallerLocation());
	}

	private async processVersion(task: SpiderTask, startTime: number) {

		if (!task.url) {
			Logger.Warning('Unexpected job data received from database', Logger.GetCallerLocation());
			return;
		}
		this._flags.MandatoryArgument = task.url;
		await this.uploadProject(task.id, task.time, startTime);

	}
}

export class CheckCommand extends Command {
	protected static _helpMessageText = 'Checks a project URL against the SearchSECO database and prints the results.';
	constructor(minerId: string, flags: Flags) {
		super(minerId, flags);
	}

	public async Execute(verbosity: Verbosity): Promise<void> {
		await this.checkProject();
	}
}

export class CheckUploadCommand extends Command {
	protected static _helpMessageText =
		'Checks a project URL against the SearchSECO database, and if the project does not exist, uploads it.';
	constructor(minerId: string, flags: Flags) {
		super(minerId, flags);
	}

	public async Execute(verbosity: Verbosity): Promise<void> {
		const checked = await this.checkProject();
		await this.uploadProject('', 0, 0);
		// await SigInt.StopProcessImmediately(this._minerId);
	}
}
