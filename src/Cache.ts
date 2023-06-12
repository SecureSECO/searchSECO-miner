import fs from "fs"
import path from "path"


type Store = {
    [key: string]: any
}

export default class Cache {
    public static Store: Store = {}
    private static readonly _path: string = path.join(__dirname, './.cache')

    public static ReadCache() {
        if (!fs.existsSync(this._path)) {
            fs.closeSync(fs.openSync(this._path, 'w'))
        } else {
            const content = fs.readFileSync(this._path).toString() || '{}'
            this.Store = JSON.parse(content)
        }
    }

    public static WriteCacheToFile() {
        fs.writeFileSync(this._path, JSON.stringify(this.Store), { encoding: 'utf8', flag: 'w' })
    }

    public static SetMinerId(id: string, status: string) {
        this.Store = {
            [id]: {
                status
            },
            ...JSON.parse(JSON.stringify(this.Store))
        }
        this.WriteCacheToFile()
    }

    public static SetMinerStatus(id: string, status: string) {
        this.Store[id].status = status
        this.WriteCacheToFile()
    }
}