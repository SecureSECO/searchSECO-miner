import HashData from './modules/searchSECO-parser/src/HashData';
import fs, { WriteStream } from 'fs';
import { AuthorData } from './modules/searchSECO-spider/src/Spider';
import path from 'path';
import {
	AuthorResponseData,
	MethodResponseData,
	ProjectResponseData,
} from './modules/searchSECO-databaseAPI/src/Response';
import DatabaseRequest, { getAuthors, transformHashList } from './DatabaseRequest';
import { ObjectMap, ObjectSet } from './Utility';

type Method = {
	method_hash: string;
	projectID: string;
	startVersion: string;
	startVersionHash: string;
	endVersion: string;
	endVersionHash: string;
	method_name: string;
	file: string;
	lineNumber: string;
	parserVersion: string;
	vulnCode: string;
	authorTotal: string;
	authorIds: string[];
};

enum OutputStream {
	SUMMARY,
	REPORT,
}

function getLongestStringLength(array: string[]): number {
	return array.reduce((currentLongest, str) => (str.length > currentLongest ? str.length : currentLongest), 0);
}

function line(str: string) {
	return `${str}\n`;
}

function parseDatabaseHashes(
	entries: Method[],
	receivedHashes: Map<string, Method[]>,
	projectMatches: Map<string, number>,
	projectVersions: ObjectSet<[string, string]>,
	authors: Map<string, number>
) {
	entries.forEach((method) => {
		if (!receivedHashes.has(method.method_hash)) receivedHashes.set(method.method_hash, []);
		receivedHashes.get(method.method_hash).push(method);

		for (let i = 0; i < parseInt(method.authorTotal); i++) {
			if (!/^[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$/.test(method.authorIds[i])) continue;

			if (!authors.has(method.authorIds[i])) authors.set(method.authorIds[i], 0);
			authors.set(method.authorIds[i], authors.get(method.authorIds[i]) + 1);
		}

		if (!projectMatches.has(method.projectID)) projectMatches.set(method.projectID, 0);
		projectMatches.set(method.projectID, projectMatches.get(method.projectID) + 1);

		if (method.startVersion) {
			projectVersions.add([method.projectID, method.startVersion]);
			if (method.startVersion != method.endVersion)
				if (method.endVersion) projectVersions.add([method.projectID, method.endVersion]);
				else console.log(method);
		} else console.log(method);
	});
}

function getDatabaseAuthorAndProjectData(
	projectEntries: ProjectResponseData[],
	authorEntries: AuthorResponseData[],
	dbProjects: Map<string, ProjectResponseData>,
	authorIdToName: Map<string, AuthorResponseData>
) {
	projectEntries.forEach((entry) => {
		dbProjects.set(entry.id, entry);
	});

	authorEntries.forEach((entry) => {
		authorIdToName.set(entry.uuid, entry);
	});
}

const WORKING_DIR = (process as any).pkg ? process.cwd() : __dirname;

export default class MatchPrinter {
	private _reportStream: WriteStream;
	private _summaryStream: WriteStream;
	private _JSONbuilder: JSONBuilder;

	constructor() {
		this._summaryStream = fs.createWriteStream(path.resolve(WORKING_DIR, './summary.txt'));
		this._reportStream = fs.createWriteStream(path.resolve(WORKING_DIR, './report.json'));
		this._JSONbuilder = new JSONBuilder();
	}

	public async PrintHashMatches(
		hashes: HashData[],
		databaseResponse: MethodResponseData[],
		authorData: AuthorData,
		url: string,
		projectID: number
	) {
		const databaseMethods = databaseResponse.map((res) => JSON.parse(JSON.stringify(res)) as Method);

		const receivedHashes = new Map<string, Method[]>();
		const projectMatches = new Map<string, number>();
		const projectVersions = new ObjectSet<[string, string]>();
		const dbAuthors = new Map<string, number>();
		const dbProjects = new Map<string, ProjectResponseData>();
		const authorIdToName = new Map<string, AuthorResponseData>();

		parseDatabaseHashes(databaseMethods, receivedHashes, projectMatches, projectVersions, dbAuthors);

		const [authorResponse, projectResponse] = await Promise.all([
			DatabaseRequest.GetAuthor(dbAuthors),
			DatabaseRequest.GetProjectData(projectVersions),
		]);

		if (authorResponse.responseCode != 200 || projectResponse.responseCode != 200) return;

		const authorEntries = authorResponse.response as AuthorResponseData[];
		const projectEntries = projectResponse.response as ProjectResponseData[];

		getDatabaseAuthorAndProjectData(projectEntries, authorEntries, dbProjects, authorIdToName);

		const transformedList = transformHashList(hashes);
		const authors = getAuthors(transformedList, authorData);

		let matches = 0;
		const authorCopiedForm = new Map<string, number>();
		const authorsCopied = new Map<string, number>();
		const vulnerabilities: [HashData, Method][] = [];

		const hashMethods = new Map<string, HashData[]>();

		hashes.forEach((hash) => {
			if (!hashMethods.has(hash.Hash)) hashMethods.set(hash.Hash, []);
			hashMethods.get(hash.Hash).push(hash);
		});

		let matchesReport = '';
		receivedHashes.forEach((methods, method_hash) => {
			if (
				methods.reduce(
					(projectMatch, currentMethod) => projectMatch + Number(currentMethod.projectID != projectID.toString()),
					0
				)
			) {
				matches++;
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
				);
			}
		});

		this._printAndWriteToFile(matchesReport);

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
		);

		this._writeLineToFile(this._JSONbuilder.Compile(), OutputStream.REPORT);
	}

	private _printMatch(
		hashes: HashData[],
		dbEntries: Method[],
		authors: ObjectMap<HashData, string[]>,
		projectID: string,
		authorCopiedForm: Map<string, number>,
		authorsCopied: Map<string, number>,
		vulnerabilities: [HashData, Method][],
		dbProjects: Map<string, ProjectResponseData>,
		authorIdToName: Map<string, AuthorResponseData>,
		report: string
	): string {
		let currentReport = report;

		const header = `Hash ${hashes[0].Hash}`;
		currentReport += `${'-'.repeat(header.length)}\n`;
		currentReport += `${header}\n`;
		currentReport += `${'-'.repeat(header.length)}\n\n`;

		this._JSONbuilder.Add(`hashes[0]`, {
			hash: hashes[0].Hash,
		});

		hashes.forEach((hash, idx) => {
			currentReport += `  * Method ${hash.MethodName} in file ${hash.FileName}, line ${hash.LineNumber}\n`;
			currentReport += `    Authors of local method: \n`;

			this._JSONbuilder.Add(`hashes[0].methods[${idx}]`, {
				name: hash.MethodName,
				file: hash.FileName,
				lineNumber: hash.LineNumber,
				isLocal: true,
			});

			const authorData = authors.get(hash) || [];
			authorData.forEach((s) => {
				const formatted = s.replace(/\?/g, '\t');
				currentReport += `  ${formatted}\n`;
				authorsCopied.set(s, (authorsCopied.get(s) || 0) + 1);

				const [username, email] = s.split('\t');
				this._JSONbuilder.Add(`hashes[0].methods[${idx}].author`, {
					username,
					email,
				});
			});

			currentReport += '\n';
		});

		currentReport += '\nDATABASE\n';
		dbEntries.forEach((method, idx) => {
			if (method.projectID === projectID) return;
			if (!dbProjects.has(method.projectID)) return;

			const linkFile = method.file.replace(/\\\\/g, '/');

			const currentProject = dbProjects.get(method.projectID);
			currentReport += `  * Method ${method.method_name} in project ${currentProject.name} in file ${method.file}, line ${method.lineNumber}\n`;
			currentReport += `    URL: ${currentProject.url}/blob/${method.endVersionHash}/${linkFile}#L${method.lineNumber}\n`;

			this._JSONbuilder.Add(
				`hashes[0].methods`,
				{
					isLocal: false,
					url: `${currentProject.url}/blob/${method.endVersionHash}/${linkFile}#L${method.lineNumber}`,
					name: method.method_name,
					file: method.file,
					lineNumber: method.lineNumber,
					project: {
						id: currentProject.id,
						name: currentProject.name,
						url: currentProject.url,
					},
				},
				true
			);

			if (method.vulnCode) {
				currentReport += `   Method marked as vulnerable with code ${method.vulnCode} (https://nvd.nist.gov/vuln/detail/${method.vulnCode})`;
				this._JSONbuilder.Add(`hashes[0].methods[${idx}].vulnCode`, method.vulnCode);
				hashes.forEach((hash) => {
					vulnerabilities.push([hash, method]);
				});
			} else this._JSONbuilder.Add(`hashes[0].methods[${idx}].vulnCode`, '');

			if (Number(method.authorTotal) > 0) {
				currentReport += `   Authors of method found in database: \n`;
				method.authorIds.forEach((id) => {
					if (!authorIdToName.has(id)) return;
					authorCopiedForm.set(id, (authorCopiedForm.get(id) || 0) + 1);
					currentReport += `   \t${authorIdToName.get(id).username}\t${authorIdToName.get(id).email}\n`;
					this._JSONbuilder.Add(
						`hashes[0].methods[${idx}].authors`,
						{
							username: authorIdToName.get(id).username,
							email: authorIdToName.get(id).email,
						},
						true
					);
				});
			}
			currentReport += '\n';
		});

		return currentReport;
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
		this._printAndWriteToFile(`\nSummary:`);

		this._printAndWriteToFile(`Checked project url: ${url}`);
		this._printAndWriteToFile(`Methods in checked project: ${methods}`);
		const percentage = ((matches * 100) / methods).toFixed(2);
		this._printAndWriteToFile(`Matches: ${matches} (${percentage}%)`);

		this._JSONbuilder
			.Add('projectURL', url)
			.Add('methodCount', methods)
			.Add('matches', matches)
			.Add('matchPercentage', percentage);

		if (vulnerabilities.length > 0) {
			this._printAndWriteToFile('\nVulnerabilities found:');
			vulnerabilities.forEach(([hashData, method]) => {
				this._printAndWriteToFile(
					`Method with hash ${hashData.Hash} was found to be vulnerable in ${
						dbProjects.get(method.projectID).name
					} with code ${method.vulnCode} (https://nvd.nist.gov/vuln/detail/${method.vulnCode})`
				);
			});
		}

		this._printAndWriteToFile('\nProjects found in database: ');
		const vprojects: [number, string, string][] = [];

		projectMatches.forEach((value, key) => {
			if (!dbProjects.has(key)) return;
			vprojects.push([value, dbProjects.get(key).name, dbProjects.get(key).url]);
		});

		const longestProjectName = getLongestStringLength(vprojects.map(([, projectName]) => projectName));

		vprojects.sort().reverse();
		vprojects.forEach(([matchCount, projectName, projectURL], idx) => {
			this._printAndWriteToFile(
				`\t${projectName}${' '.repeat(
					longestProjectName - projectName.length - matchCount.toString().length + 5
				)}${matchCount} (${projectURL})`
			);
		});

		const localAuthors: [number, string, string][] = [];
		authorsCopied.forEach((value, key) => {
			const author = key.split('?');
			localAuthors.push([value, author[1], author[2]]);
		});

		const remoteAuthors: [number, string, string][] = [];
		authorCopiedForm.forEach((value, key) => {
			const author = authorIdToName.get(key);
			remoteAuthors.push([value, author.username, author.email]);
		});

		const longestAuthorName = getLongestStringLength([
			...localAuthors.map(([, authorName]) => authorName),
			...remoteAuthors.map(([, authorName]) => authorName),
		]);

		localAuthors.sort().reverse();
		remoteAuthors.sort().reverse();

		this._printAndWriteToFile('\nLocal authors present in matches:');
		localAuthors.forEach(([matchCount, authorName, authorEmail]) => {
			this._printAndWriteToFile(
				`\t${authorName}${' '.repeat(
					longestAuthorName - authorName.length - matchCount.toString().length + 5
				)}${matchCount} ${authorEmail}`
			);
		});

		this._printAndWriteToFile('\nAuthors present in database matches:');
		remoteAuthors.forEach(([matchCount, authorName, authorEmail]) => {
			this._printAndWriteToFile(
				`\t${authorName}${' '.repeat(
					longestAuthorName - authorName.length - matchCount.toString().length + 5
				)}${matchCount} ${authorEmail}`
			);
		});
		this._printAndWriteToFile('\n');
	}

	private _writeLineToFile(str: string, outputStream: OutputStream = OutputStream.SUMMARY) {
		const stream = (() => {
			switch (outputStream) {
				case OutputStream.SUMMARY:
					return this._summaryStream;
				case OutputStream.REPORT:
					return this._reportStream;
			}
		})();

		stream.cork();
		stream.write(line(str));
		process.nextTick(() => stream.uncork());
	}
	private _printAndWriteToFile(str: string, outputStream: OutputStream = OutputStream.SUMMARY) {
		console.log(str);
		this._writeLineToFile(str, outputStream);
	}

	public Close() {
		this._summaryStream.close();
		this._reportStream.close();
	}
}

interface JSONObject {
	[key: string]: any;
}

class JSONBuilder {
	private _object: JSONObject;
	constructor() {
		this._object = {};
	}

	public Compile(): string {
		return JSON.stringify(this._object, null, 2);
	}

	public Add(keyPattern: string, value: any, isArray = false): this {
		const keys = keyPattern.split('.');
		let reference: any = this._object;
		keys.forEach((key, idx) => {
			let index = -1;
			if (key.includes('[')) {
				index = Number(/(?<=\[).+?(?=\])/.exec(key)[0]);
				key = key.replace(/\[.+\]/, '');
			}

			if (!Object.keys(reference).includes(key))
				reference[key] = index > -1 || (idx == keys.length - 1 && isArray) ? [] : {};

			if (idx == keys.length - 1) {
				if (isArray || index > -1) reference[key].push(value);
				else reference[key] = value;
				return;
			}

			reference = reference[key];
			if (index > -1) {
				if (!reference[index]) reference[index] = {};
				reference = reference[index];
			}
		});
		return this;
	}
}
