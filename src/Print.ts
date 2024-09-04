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
import Logger from './modules/searchSECO-logger/src/Logger';
import { AuthorInfoResponseItem, CheckResponse, ProjectInfoResponseItem } from './JsonRequest';


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

class ProjectAuthorInfo {
	name: string;
	email: string;

	constructor(name: string, email: string) {
		this.name = name;
		this.email = email;
	}
}

function idFromProjectMethod(method: HashData): string {
	return method.FileName + method.LineNumber
}

function getAuthorsPerMethod(hashes: Map<string, HashData[]>, rawData: AuthorData): Map<string, string[]> {
	const output = new Map<string, string[]>();

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
					let key = idFromProjectMethod(hashesFromFile[hashesIndex]);
					if (!output.has(key)) output.set(key, []);
					output.get(key).push(toAdd);
					dupes.set(toAdd, 1);
				}
			}
			authorIndex++;
		}
	});

	return output;
}



function parseDatabaseHashes(
	methods: CheckResponse[],
	methodsPerHash: Map<string, CheckResponse[]>,
	projectOccurrence: Map<number, number>,
	projectVersions: ObjectSet<[number, number]>,
	authorOccurence: Map<string, number>
) {
	methods.forEach((method) => {
		if (!methodsPerHash.has(method.mh)) methodsPerHash.set(method.mh, []);
		methodsPerHash.get(method.mh).push(method);
		let authorTotal = method.authors.length;
		for (let i = 0; i < authorTotal; i++) {
			if (!authorOccurence.has(method.authors[i])) authorOccurence.set(method.authors[i], 0);
			authorOccurence.set(method.authors[i], authorOccurence.get(method.authors[i]) + 1);
		}

		if (!projectOccurrence.has(method.pid)) projectOccurrence.set(method.pid, 0);
		projectOccurrence.set(method.pid, projectOccurrence.get(method.pid) + 1);

		if (method.sv_time) {
			projectVersions.add([method.pid, method.sv_time]);
			if (method.sv_time != method.ev_time)
				if (method.ev_time) projectVersions.add([method.pid, method.ev_time]);
				else console.log(method);
		}
	});
}

function makeAuthorMap(
	authorEntries: AuthorInfoResponseItem[],
	authorIdToName: Map<string, AuthorInfoResponseItem>
) {
	authorEntries.forEach((entry) => {
		authorIdToName.set(entry.id, entry);
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
		projectUrl: string,
		projectID: number,
		projectMethods: HashData[],
		projectBlaming: AuthorData,
		dbMethods: CheckResponse[],
		dbProjectInfo: Map<number, ProjectInfoResponseItem[]>,
		dbAuthorInfo: AuthorInfoResponseItem[]

	) {
		const dbMethodsPerHash = new Map<string, CheckResponse[]>();
		const dbProjectOccurrence = new Map<number, number>();
		const dbProjectVersions = new ObjectSet<[number, number]>();
		const dbAuthorOccurrence = new Map<string, number>();
		const dbAuthorPerId = new Map<string, AuthorInfoResponseItem>();

		parseDatabaseHashes(dbMethods, dbMethodsPerHash, dbProjectOccurrence, dbProjectVersions, dbAuthorOccurrence);
		makeAuthorMap(dbAuthorInfo, dbAuthorPerId);

		const projectMethodsPerFile = transformHashList(projectMethods);

		// map from method to strings of 'author?author-mail'		
		const projectAuthorInfoPerMethod =
			// The map is expensive, because every key use means serialising the method to a json representation.
			// Using the Hash value alone as key is not good enough, as small methods can and do lead to the same hash values.
			// But FileName-LineNumber should be unique within the project
			//getAuthors(projectMethodsPerFile, projectBlaming);
			getAuthorsPerMethod(projectMethodsPerFile, projectBlaming);

		let matches = 0;
		const authorCopiedForm = new Map<string, number>();
		const authorsCopied = new Map<string, number>();
		const vulnerabilities: [HashData, CheckResponse][] = [];

		const projectMethodsPerHash = new Map<string, HashData[]>();

		projectMethods.forEach((hash) => {
			if (!projectMethodsPerHash.has(hash.Hash))
				projectMethodsPerHash.set(hash.Hash, []);
			//else
			//	Logger.Info(`Multiple methods in project with same hash ${hash.Hash}, name ${hash.MethodName}, file ${hash.FileName}, line ${hash.LineNumber}`, Logger.GetCallerLocation());
			projectMethodsPerHash.get(hash.Hash).push(hash);
		});


		let matchesReport = '';
		dbMethodsPerHash.forEach((methods, method_hash) => {
			if (
				methods.reduce(
					(projectMatch, currentMethod) => projectMatch + Number(currentMethod.pid != projectID),
					0
				)
			) {
				matches++;
				matchesReport = this._printMatch(
					projectMethodsPerHash.get(method_hash),
					methods,
					projectAuthorInfoPerMethod,
					projectID,
					authorCopiedForm,
					authorsCopied,
					vulnerabilities,
					dbProjectInfo,
					dbAuthorPerId,
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
			projectMethods.length,
			dbProjectInfo,
			dbAuthorPerId,
			dbProjectOccurrence,
			projectUrl
		);


		this._writeLineToFile(this._JSONbuilder.Compile(), OutputStream.REPORT);
	}

	private _printMatch(
		hashes: HashData[],
		dbEntries: CheckResponse[],
		authors: Map<string, string[]>,
		projectID: number,
		authorCopiedForm: Map<string, number>,
		authorsCopied: Map<string, number>,
		vulnerabilities: [HashData, CheckResponse][],
		dbProjects: Map<number, ProjectInfoResponseItem[]>,
		authorIdToName: Map<string, AuthorInfoResponseItem>,
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

			const authorData = authors.get(idFromProjectMethod(hash)) || [];
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
			if (method.pid === projectID) return;
			if (!dbProjects.has(method.pid)) return;

			const linkFile = method.file.replace(/\\\\/g, '/');

			let currentProject = dbProjects.get(method.pid).find((el) => el.vtime === method.ev_time);
			if (!currentProject) {
				Logger.Warning(`PrintMatch: no project found for method ${method.method} with process id ${method.pid}`, Logger.GetCallerLocation());
				currentProject = { "name": "<undefined>", "url": "<undefined>", pid: -1, vtime: -1, vhash: "<undefined>", license: "<undefined>", oid: "", pv: -1 };
			}
			currentReport += `  * Method ${method.method} in project ${currentProject.name} in file ${method.file}, line ${method.line}\n`;
			currentReport += `    URL: ${currentProject.url}/blob/${method.ev_hash}/${linkFile}#L${method.line}\n`;

			this._JSONbuilder.Add(
				`hashes[0].methods`,
				{
					isLocal: false,
					url: `${currentProject.url}/blob/${method.ev_hash}/${linkFile}#L${method.line}`,
					name: method.method,
					file: method.file,
					lineNumber: method.line,
					project: {
						id: currentProject.pid,
						name: currentProject.name,
						url: currentProject.url,
					},
				},
				true
			);

			if (method.vuln) {
				currentReport += `   Method marked as vulnerable with code ${method.vuln} (https://nvd.nist.gov/vuln/detail/${method.vuln})`;
				this._JSONbuilder.Add(`hashes[0].methods[${idx}].vulnCode`, method.vuln);
				hashes.forEach((hash) => {
					vulnerabilities.push([hash, method]);
				});
			} else this._JSONbuilder.Add(`hashes[0].methods[${idx}].vulnCode`, '');

			let authorTotal = method.authors.length;
			if (authorTotal > 0) {
				currentReport += `   Authors of method found in database: \n`;
				method.authors.forEach((id) => {
					if (!authorIdToName.has(id)) return;
					authorCopiedForm.set(id, (authorCopiedForm.get(id) || 0) + 1);
					currentReport += `   \t${authorIdToName.get(id).name}\t${authorIdToName.get(id).mail}\n`;
					this._JSONbuilder.Add(
						`hashes[0].methods[${idx}].authors`,
						{
							username: authorIdToName.get(id).name,
							email: authorIdToName.get(id).mail,
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
		vulnerabilities: [HashData, CheckResponse][],
		matches: number,
		methods: number,
		dbProjects: Map<number, ProjectInfoResponseItem[]>,
		authorIdToName: Map<string, AuthorInfoResponseItem>,
		projectMatches: Map<number, number>,
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
					`Method with hash ${hashData.Hash} was found to be vulnerable in ${dbProjects.get(method.pid)[0].name
					} with code ${method.vuln} (https://nvd.nist.gov/vuln/detail/${method.vuln})`
				);
			});
		}

		this._printAndWriteToFile('\nProjects found in database: ');
		const vprojects: [number, string, string][] = [];

		projectMatches.forEach((value, key) => {
			if (!dbProjects.has(key)) return;
			let aProject = dbProjects.get(key)[0];
			vprojects.push([value, aProject.name, aProject.url]);
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
			remoteAuthors.push([value, author.name, author.mail]);
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
