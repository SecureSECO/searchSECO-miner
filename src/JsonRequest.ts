import HashData from './modules/searchSECO-parser/src/HashData';
import Logger from './modules/searchSECO-logger/src/Logger';
import config from './config/config'
import { CrawlData, ProjectMetadata } from './modules/searchSECO-crawler/src/Crawler';
import { AuthorData } from './modules/searchSECO-spider/src/Spider';
import { PARSER_VERSION } from './modules/searchSECO-parser/src/Parser';
import { ObjectMap } from './Utility';


const dbapi_url = config.JSON_URL;

const token = config.JSON_TOKEN;


interface CheckRequest {
    Check: string[];
}

interface MethodInFile {
    file: string;
    line: number;
    pid: string;
    project_versions: number[];
}

export type CheckResponse = {
    mh: string;
    pid: number;
    method: string;
    sv_time: number;
    sv_hash: string;
    ev_time: number;
    ev_hash: string;
    file: string;
    line: number;
    pv: number;
    vuln: string | null;
    authors: string[];
};

export interface ProjectWithVersion {
    project_id: number;
    version: number;
}

interface ProjectInfoRequest {
    ProjectInfo: [ProjectWithVersion[], boolean];
}

export type ProjectInfoResponseItem = {
    pid: number,
    vtime: number,
    vhash: string,
    license: string,
    name: string,
    url: string,
    oid: string,
    pv: number,
    hashes?: string[]
}

interface AuthorRequest {
    AuthorInfo: string[];
}

export type AuthorInfoResponseItem = {
    name: string,
    mail: string,
    id: string
}

interface GetTaskRequest {
    GetTask: string[];
}

export interface SpiderTask {
    id: string,
    url: string,
    time: number,
    timeout: number
}
export interface CrawlTask {
    id: number,
    time_lc: number
}

interface Author {
    name: string,
    mail: string
}

interface MethodData {
    hash: string,
    name: string,
    file: string,
    line: number,
    authors: Author[],
    vuln: null | string,
}

interface Upload {
    project_id: number,
    version: number,
    version_hash: string,
    license: string,
    project_name: string,
    url: string,
    owner_name: string,
    owner_mail: string,
    parser_version: number,
    prev_version: null | { version: number, unchanged_files: string[] },
    method_data: MethodData[]
}

interface JobFinish {
    jid: string,
    time: number,
    reason: number,
    rdata: string
}


export type Task = "No" | { "Spider": SpiderTask } | { "Crawl": CrawlTask };

interface NewJob { url: string, prio: number, timeout: number }

interface CrawlerData { id: number, time_lc: number, jobs: NewJob[] }

interface CrawlJobsRequest { CrawlJobs: CrawlerData }

interface PrevProjectsRequest { "PrevProjects": number[] }

interface UpdateJobRequest { "UpdateJob": { "jid": string, "time": number } }

interface UploadRequest { "Upload": Upload }

interface FinishJobRequest { "FinishJob": JobFinish }

type Content =
    CheckRequest | ProjectInfoRequest | AuthorRequest |
    GetTaskRequest | CrawlJobsRequest | PrevProjectsRequest | UpdateJobRequest |
    UploadRequest | FinishJobRequest;




interface Request {
    token: string;
    content: Content;
}

function toJobs(crawlData: CrawlData): NewJob[] {
    let result: NewJob[] = [];
    Logger.Debug(`Converting ${crawlData.URLImportanceList.length} jobs`, Logger.GetCallerLocation());
    crawlData.URLImportanceList.map(v => { result.push({ url: v.url, prio: v.importance, timeout: v.finalProjectId }) })
    return result;
}

export class JsonRequest {

    static async PerformRequest(content: Content): Promise<Object> {
        let req: Request = {
            'token': token,
            'content': content
        }
        const body = JSON.stringify(req);
        Logger.Debug(`Performing request to ${dbapi_url} with body ${body}`, Logger.GetCallerLocation());
        const response: Response = await fetch(dbapi_url, {
            method: 'POST',
            body,
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
            },
        });
        Logger.Debug(`Status code: ${response.status}`, Logger.GetCallerLocation());

        if (!response.ok) {
            Logger.Warning(`JSON api status code: ${response.status}`, Logger.GetCallerLocation());
            throw new Error(`Error! status: ${response.status}`);
        }

        const obj: Object = (await response.json());
        return obj;
    }

    public static async FindMatches(hashes: string[]): Promise<CheckResponse[]> {
        Logger.Debug(`In FindMatches (JsonRequest)`, Logger.GetCallerLocation());
        let content: Content = {
            'Check': hashes
        }
        try {
            let obj = await this.PerformRequest(content);
            const pr = obj as CheckResponse[];
            if (pr.length > 0) {
                const md0 = JSON.stringify(pr[0], null, 4);
                Logger.Debug(`First CheckResponse:  ${md0}`, Logger.GetCallerLocation());
            }
            return pr;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
        Logger.Debug(`First CheckResponse returning empty result`, Logger.GetCallerLocation());
        return [];
    }



    public static async GetProjectData(pireq: ProjectWithVersion[]): Promise<ProjectInfoResponseItem[]> {
        let content: Content = {
            'ProjectInfo': [pireq, false]
        }
        try {
            let obj = await this.PerformRequest(content);
            let result = obj as ProjectInfoResponseItem[];
            return result;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
        return []
    }

    public static async GetAuthorData(authorIds: Iterable<string>): Promise<AuthorInfoResponseItem[]> {
        const authorArray = Array.from(authorIds)
        let content: Content = { 'AuthorInfo': authorArray };
        try {
            let obj = await this.PerformRequest(content);
            let result = obj as AuthorInfoResponseItem[];
            return result;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
        return []
    }

    public static async GetTask(): Promise<Task> {
        Logger.Debug(`In GetTask (JsonRequest)`, Logger.GetCallerLocation());
        let content: Content = { "GetTask": [] };
        try {
            let obj = await this.PerformRequest(content);
            const pr = obj as Task;
            Logger.Debug(`In GetTask (returning value)`, Logger.GetCallerLocation());
            return pr;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
        Logger.Debug(`First CheckResponse returning empty result`, Logger.GetCallerLocation());
        return "No";
    }



    public static async AddCrawledJobs(crawled: CrawlData, task: CrawlTask) {
        let jobs = toJobs(crawled);
        let content = { "CrawlJobs": { "id": task.id, "time_lc": task.time_lc, jobs } };
        try {
            let obj = await this.PerformRequest(content);
            const pr = obj as Task;
            return pr;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
        Logger.Debug(`First CheckResponse returning empty result`, Logger.GetCallerLocation());
        return "No";
    }

    public static async LastVersion(projectId: number): Promise<number> {
        let content = { "PrevProjects": [projectId] };
        try {
            let obj = await this.PerformRequest(content);
            const pr = obj as ProjectInfoResponseItem[];
            if (pr.length == 0)
                return -1;
            else
                return pr[0].vtime;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
    }

    public static async UpdateJob(jid: string, time: number): Promise<void> {
        let content = { "UpdateJob": { jid, time } }
        try {
            let obj = await this.PerformRequest(content);
            return;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
    }

    public static async UploadHashes(
        hashes: HashData[],
        metadata: ProjectMetadata,
        authordata: AuthorData,
        prevCommitTime: number,
        unchangedFiles: string[]
    ): Promise<boolean> {
        let prev_version = null;
        if (prevCommitTime > 0) {
            prev_version = { version: prevCommitTime, unchanged_files: unchangedFiles }
        }
        let hashes2: MethodData[] = [];
        const transformedHashList = transformHashList(hashes);
        const authors = getAuthors(transformedHashList, authordata);
        hashes.map((val, _ix, _arr) => { hashes2.push({ hash: val.Hash, name: val.MethodName, file: val.FileName, line: val.LineNumber, vuln: val.VulnCode, authors: authors.get(val) }) })
        let content = {
            "Upload": {
                project_id: metadata.id,
                version: metadata.versionTime,
                version_hash: metadata.versionHash,
                license: metadata.license,
                project_name: metadata.name,
                url: metadata.url,
                owner_name: metadata.authorName,
                owner_mail: metadata.authorMail,
                parser_version: PARSER_VERSION,
                prev_version,
                method_data: hashes2

            }
        }
        try {
            let obj = await this.PerformRequest(content);
            return;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }
    }

    public static async finishJob(jid: string, time: number, reason: number, rdata: string): Promise<number> {
        let content = {
            "FinishJob": { jid: jid, time: time, reason: reason, rdata: rdata }
        };
        try {
            let obj = await this.PerformRequest(content);
            return;
        } catch (error) {
            if (error instanceof Error) {
                Logger.Warning(`error message:  ${error.message}`, Logger.GetCallerLocation());
                throw error;
            } else {
                Logger.Warning(`unexpected error: $error`, Logger.GetCallerLocation());
                throw 'An unexpected error occurred';
            }
        }

    }

}

function getAuthors(hashes: Map<string, HashData[]>, rawData: AuthorData): ObjectMap<HashData, Author[]> {
    const output = new ObjectMap<HashData, Author[]>();
    // process each file (key)
    rawData.forEach((_, key) => {
        let currentEnd = -1,
            hashesIndex = -1,
            authorIndex = 0;
        const dupes = new Map<string, number>();

        const hashesFromFile = hashes.get(key);
        const rawAuthorData = rawData.get(key);
        // The CodeBlocks are sorted by increasing "line" value

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
                    output.get(hashesFromFile[hashesIndex]).push({ name: author, mail });
                    dupes.set(toAdd, 1);
                }
            }
            authorIndex++;
        }
    });

    return output;
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


