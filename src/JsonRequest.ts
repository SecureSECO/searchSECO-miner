import HashData from './modules/searchSECO-parser/src/HashData';
import Logger from './modules/searchSECO-logger/src/Logger';
import config from './config/config'


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
    ProjectInfo: ProjectWithVersion[];
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

type Content =
    CheckRequest | ProjectInfoRequest | AuthorRequest;


interface Request {
    token: string;
    content: Content;
}

export class JsonRequest {

    static async PerformRequest(content: Content): Promise<Object> {
        let req: Request = {
            'token': token,
            'content': content
        }
        const response: Response = await fetch(dbapi_url, {
            method: 'POST',
            body: JSON.stringify(req),
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
            },
        });

        if (!response.ok) {
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
            'ProjectInfo': pireq
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

}

