/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { TCPClient } from './modules/searchSECO-databaseAPI/src/Client';
import { CrawlData, ProjectMetadata } from './modules/searchSECO-crawler/src/Crawler';
import config from './config/config';
import { AuthorData } from './modules/searchSECO-spider/src/Spider';
import HashData from './modules/searchSECO-parser/src/HashData';
import Logger, { Verbosity } from './modules/searchSECO-logger/src/Logger';
import { RequestType } from './modules/searchSECO-databaseAPI/src/Request';
import Error, { ErrorCode } from './Error';
import { MethodResponseData, TCPResponse } from './modules/searchSECO-databaseAPI/src/Response';
import { ObjectMap, ObjectSet } from './Utility';
import { PARSER_VERSION } from './modules/searchSECO-parser/src/Parser';
import cassandra from 'cassandra-driver';

/**
 * Serializes all data found to an array of strings to be sent to the database
 * @param data The hashdata extracted
 * @param metadata The metadata
 * @param authors The author data
 * @param prevCommitTime The previous cmmit time
 * @param unchangedFiles All unchanged files between commits
 * @returns An array with all items to send to the database
 */
function serializeData(
	data: HashData[],
	metadata: ProjectMetadata,
	authors: AuthorData,
	prevCommitTime: string,
	unchangedFiles: string[]
): string[] {
	const header = generateHeaderFromMetadata(metadata);
	const transformedHashList = transformHashList(data);
	const authorSendData = getAuthors(transformedHashList, authors);
	return [
		header,
		prevCommitTime,
		unchangedFiles
			.join('?')
			.replace(/\\|\\\\/g, '/')
			.replace(/.\//g, ''),
		...hashDataToString(data, authorSendData),
	];
}

export function transformHashList(data: HashData[]): Map<string, HashData[]> {
	const output = new Map<string, HashData[]>();
	data.forEach((hash) => {
		if (!output.has(hash.FileName)) output.set(hash.FileName, []);
		output.get(hash.FileName).push(hash);

		if (output.get(hash.FileName).length > 1) {
			const lastLineNumber = output.get(hash.FileName)[output.get(hash.FileName).length - 1].LineNumber;
			const beforeLastLineNumber = output.get(hash.FileName)[output.get(hash.FileName).length - 2].LineNumber;
			if (lastLineNumber < beforeLastLineNumber) {
				const smaller = output.get(hash.FileName).pop();
				const bigger = output.get(hash.FileName).pop();
				output.get(hash.FileName).push(smaller, bigger);
			}
		}
	});

	return output;
}

export function getAuthors(hashes: Map<string, HashData[]>, rawData: AuthorData): ObjectMap<HashData, string[]> {
	const output = new ObjectMap<HashData, string[]>();

	rawData.forEach((_, key) => {
		let currentEnd = -1,
			hashesIndex = -1,
			authorIndex = 0;
		const dupes = new Map<string, number>();

		const hashesFromFile = hashes.get(key);
		const rawAuthorData = rawData.get(key);

		while (hashesIndex < hashesFromFile.length || authorIndex < rawAuthorData.length) {
			if (authorIndex == rawAuthorData.length || currentEnd < rawAuthorData[authorIndex].line) {
				hashesIndex++;
				if (hashesIndex >= hashesFromFile.length) break;
				if (authorIndex > 0) authorIndex--;
				currentEnd = hashesFromFile[hashesIndex].LineNumberEnd;
				dupes.clear();
			}
			if (
				hashesFromFile[hashesIndex].LineNumber <=
				rawAuthorData[authorIndex].line + rawAuthorData[authorIndex].numLines
			) {
				const cd = rawAuthorData[authorIndex];
				const author = cd.commit.author.replace(/\?/g, '');
				const mail = cd.commit.authorMail.replace(/\?/g, '');
				const toAdd = `?${author}?${mail}`;

				if ((dupes.get(toAdd) || 0) == 0) {
					if (!output.has(hashesFromFile[hashesIndex])) output.set(hashesFromFile[hashesIndex], []);
					output.get(hashesFromFile[hashesIndex]).push(toAdd);
					dupes.set(toAdd, 1);
				}
			}
			authorIndex++;
		}
	});

	return output;
}

function generateHeaderFromMetadata(metadata: ProjectMetadata) {
	const arr = Object.keys(metadata)
		.filter((key) => key !== 'defaultBranch')
		.map((key) => {
			return metadata[key as keyof ProjectMetadata] || '';
		});
	arr.push(PARSER_VERSION);
	return arr.join('?');
}

function hashDataToString(hashData: HashData[], authors: ObjectMap<HashData, string[]>): string[] {
	return hashData.map((item) => {
		const authorArray = authors.get(item) || [];
		return [
			item.Hash,
			item.MethodName || '-',
			item.FileName.replace(/\\/g, '/').replace('./', ''),
			item.LineNumber,
			`${authorArray.length}${authorArray.join('')}`.replace(/&lt;/g, '<').replace(/&gt;/g, '>'),
			`${item.VulnCode || ''}`,
		]
			.filter((s) => s !== '')
			.join('?');
	});
}

function serializeCrawlData(urls: CrawlData, id: string): string[] {
	const result: string[] = [];

	result.push(`${urls.finalProjectId}?${id}`);

	const langs = Object.keys(urls.languages)
		.map((lang) => `${lang}?${urls.languages[lang]}`)
		.join('?');

	result.push(langs);

	urls.URLImportanceList.forEach(({ url, importance, finalProjectId }) => {
		result.push(`${url}?${importance}?${finalProjectId}`);
	});

	return result;
}

function serializeAuthorData(authors: Map<string, number>): string[] {
	return Array.from(authors.keys());
}

function serializeProjectData(projects: ObjectSet<[string, string]>): string[] {
	const result: string[] = [];
	projects.forEach(([first, second]) => result.push(`${first}?${second}`));
	return result;
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
	TIMEOUT,
}

export default class DatabaseRequest {
	private static _client = new TCPClient('client', config.DB_HOST, config.DB_PORT);
	private static _minerId = '';
	private static _cassandraClient = new cassandra.Client({
		contactPoints: [`${config.DB_HOST}:8002`],
		localDataCenter: 'dcscience-vs317.science.uu.nl',
		authProvider: new cassandra.auth.PlainTextAuthProvider('cassandra', 'cassandra'),
		keyspace: 'rewarding',
	});

	public static SetMinerId(id: string) {
		this._minerId = id;
	}

	public static SetVerbosity(verbosity: Verbosity) {
		Logger.SetVerbosity(verbosity);
		this.updateClientVerbosity(verbosity);
	}

	private static updateClientVerbosity(verbosity: Verbosity) {
		this._client = new TCPClient('client', config.DB_HOST, config.DB_PORT, verbosity);
	}

	public static async ConnectToCassandraNode() {
		await this._cassandraClient.connect();
		Logger.Debug('Successfully connected to Cassandra', Logger.GetCallerLocation());
	}

	public static async UploadHashes(
		hashes: HashData[],
		metadata: ProjectMetadata,
		authordata: AuthorData,
		prevCommitTime: string,
		unchangedFiles: string[]
	): Promise<boolean> {
		const raw = serializeData(hashes, metadata, authordata, prevCommitTime, unchangedFiles);
		Logger.Info(`Uploading ${hashes.length} methods to the database`, Logger.GetCallerLocation(), true);
		const { responseCode } = await this._client.Execute(RequestType.UPLOAD, raw);
		if (responseCode == 200) await this.incrementClaimableHashes(hashes.length);
		else
			Logger.Warning(
				`Skipping addition of ${hashes.length} hashes to the claimable hashcount`,
				Logger.GetCallerLocation()
			);

		return responseCode === 200;
	}

	public static async GetAuthor(authors: Map<string, number>) {
		return await this._client.Execute(RequestType.GET_AUTHOR, serializeAuthorData(authors));
	}

	public static async GetProjectData(projectVersions: ObjectSet<[string, string]>) {
		return await this._client.Execute(RequestType.EXTRACT_PROJECTS, serializeProjectData(projectVersions));
	}

	public static async AddCrawledJobs(crawled: CrawlData, id: string): Promise<TCPResponse> {
		return await this._client.Execute(RequestType.UPLOAD_CRAWL_DATA, serializeCrawlData(crawled, id));
	}

	public static async GetProjectVersion(id: string, versionTime: string): Promise<number> {
		Logger.Debug(`Getting previous project`, Logger.GetCallerLocation());
		const { responseCode, response } = await this._client.Execute(RequestType.GET_PREVIOUS_PROJECT, [
			`${id}?${versionTime}`,
		]);
		if (response.length == 0 || responseCode != 200) return 0;
		return parseInt((response[0] as { raw: string }).raw.split('\n')[0].split('?')[0]) || 0;
	}

	public static async GetNextJob(): Promise<string> {
		Logger.Debug('Retrieving new job', Logger.GetCallerLocation());
		const { response } = await this._client.Execute(RequestType.GET_TOP_JOB, []);
		return (response[0] as { raw: string }).raw;
	}

	public static async UpdateJob(jobID: string, jobTime: string): Promise<string> {
		const { response } = await this._client.Execute(RequestType.UPDATE_JOB, [`${jobID}?${jobTime}`]);
		return (response[0] as { raw: string }).raw as string;
	}

	public static async FinishJob(jobID: string, jobTime: string, code: FinishReason, message: string) {
		if (Error.Code != ErrorCode.HANDLED_ERRNO) {
			Error.Code = 0;
			await this._client.Execute(RequestType.FINISH_JOB, [jobID, jobTime, code.toString(), message]);
			if (Error.Code == 0) {
				Error.Code = ErrorCode.HANDLED_ERRNO;
			}
		}
	}

	public static async FindMatches(hashes: HashData[]): Promise<MethodResponseData[]> {
		const data = Array.from(new Set<string>(hashes.map((hash) => hash.Hash)));
		const { response, responseCode } = await this._client.Execute(RequestType.CHECK, data);
		if (responseCode == 200) return response as MethodResponseData[];
		return [];
	}

	public static async RetrieveClaimableHashCount(): Promise<cassandra.types.Long> {
		Logger.Debug('Connecting with the database to retrieve all claimable hashes', Logger.GetCallerLocation());
		const query = 'SELECT claimable_hashes FROM miners WHERE id=? AND wallet=?;';
		const result = await this._cassandraClient.execute(
			query,
			[cassandra.types.Uuid.fromString(this._minerId), config.PERSONAL_WALLET_ADDRESS],
			{ prepare: true }
		);
		return result.rows[0]?.claimable_hashes || 0;
	}

	private static async incrementClaimableHashes(amount: number) {
		Logger.Debug(`Incrementing claimable hash count by ${amount}`, Logger.GetCallerLocation());
		const currentCount = await this.RetrieveClaimableHashCount();
		const newCount = currentCount.add(cassandra.types.Long.fromNumber(amount));
		const query = 'UPDATE rewarding.miners SET claimable_hashes=?, last_hashes_update=? WHERE id=? AND wallet=?;';
		await this._cassandraClient.execute(
			query,
			[
				newCount,
				cassandra.types.Long.fromNumber(Date.now()),
				cassandra.types.Uuid.fromString(this._minerId),
				config.PERSONAL_WALLET_ADDRESS,
			],
			{ prepare: true }
		);
		Logger.Debug(`Total of claimable hashes is now ${newCount.low}`, Logger.GetCallerLocation());
	}

	public static async ResetClaimableHashCount() {
		Logger.Debug('Resetting claimable hash count', Logger.GetCallerLocation());
		const query = 'UPDATE rewarding.miners SET claimable_hashes=? WHERE wallet=?;';
		await this._cassandraClient.execute(query, [0, config.PERSONAL_WALLET_ADDRESS], { prepare: true });
	}

	public static async AddMinerToDatabase(id: string, wallet: string): Promise<boolean> {
		const query =
			'INSERT INTO rewarding.miners (id, wallet, claimable_hashes, last_startup, status) VALUES (?, ?, ?, ?, ?) IF NOT EXISTS;';
		const result = await this._cassandraClient.execute(
			query,
			[
				cassandra.types.Uuid.fromString(id),
				wallet,
				cassandra.types.Long.fromNumber(0),
				cassandra.types.Long.fromNumber(Date.now()),
				'running',
			],
			{ prepare: true }
		);
		return result.rows[0]['[applied]'];
	}

	public static async SetMinerStatus(id: string, status: string) {
		const query = 'UPDATE rewarding.miners SET status=?, last_startup=? WHERE id=? AND wallet=?;';
		Logger.Debug(`Setting miner status to ${status}`, Logger.GetCallerLocation());
		await this._cassandraClient.execute(
			query,
			[
				status,
				cassandra.types.Long.fromNumber(Date.now()),
				cassandra.types.Uuid.fromString(id),
				config.PERSONAL_WALLET_ADDRESS,
			],
			{ prepare: true }
		);
	}

	public static async ListMinersAssociatedWithWallet(wallet: string): Promise<{ id: string; status: string }[]> {
		const query = 'SELECT id, status FROM rewarding.miners WHERE wallet=? ALLOW FILTERING;';
		Logger.Debug(`List all miners associated with wallet ${wallet}`, Logger.GetCallerLocation());
		const response = await this._cassandraClient.execute(query, [wallet]);

		return response.rows.map((row) => ({
			id: row.id.toString(),
			status: row.status.toString(),
		}));
	}

	public static async TruncateZombieMiners(wallet: string): Promise<void> {
		let query =
			'SELECT id, claimable_hashes, last_hashes_update, last_startup, status FROM rewarding.miners WHERE wallet=? AND status=? ALLOW FILTERING;';
		const response = await this._cassandraClient.execute(query, [wallet, 'running']);

		const dayInMilis = 86_400_000;
		const deadMinerIds = response.rows
			.filter(({ last_hashes_update, last_startup, status }) => {
				const isOneDayOld = parseInt(last_startup) + dayInMilis >= Date.now();
				const hasUpdatedWithinOneDay = Math.abs(parseInt(last_hashes_update) - Date.now()) <= dayInMilis;
				return isOneDayOld && !hasUpdatedWithinOneDay && status === 'running';
			})
			.map(({ id }) => id);

		if (deadMinerIds.length == 0) return;

		query = `UPDATE rewarding.miners SET status=? WHERE id IN (${new Array(deadMinerIds.length)
			.fill('?')
			.join(',')}) AND wallet=?;`;
		await this._cassandraClient.execute(query, ['idle', ...deadMinerIds, wallet]);
	}
}
