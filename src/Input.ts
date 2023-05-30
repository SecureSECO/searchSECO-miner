

enum FlagName {
    HELP = "Help",
    VERSION = "Version",
    VERBOSE = "Verbose",
    COMMAND = "Command"
}

const shorthandToLongMapping: Map<string, FlagName> = new Map<string, FlagName>([
    ["h", FlagName.HELP],
    ["v", FlagName.VERSION],
    ["V", FlagName.VERBOSE],
])

export class Flags {
    public MandatoryArgument: string = ""
    public CPU: number = 1
    public Verbose: number = 4
    public Help: boolean = false
    public Version: boolean = false
    public GithubUser: string = ""
    public GithubToken: string = ""
    public Branch: string = ""
    public WorkerName: string = ""
    public VulnerabilityCode: string = ""
    public Lines: string = ""
    public ProjectCommit: string = ""
    public Code: string = ""
    public Commit: string = ""
}

export class ParsedInput {
    public Command: string
    public Flags: Flags
    public ExecutablePath: string
    constructor(command: string, flags: Flags, execPath: string) {
        this.Command = command
        this.Flags = flags,
        this.ExecutablePath = execPath
    }
}

type UserInput = {
    [key: string]: any
}

export class InputParser {
    static Parse(input: UserInput): ParsedInput {

        const flags: any = {...new Flags()}

        Object.keys(input).forEach((key: keyof UserInput) => {
            if (key.toString() === "$0")
                return

            if (key.toString() === "_") {
                flags.MandatoryArgument = input[key][0]
                return
            }

            if (key.toString().length == 1 && shorthandToLongMapping.has(key.toString())) {
                const flagName = shorthandToLongMapping.get(key.toString())
                flags[flagName] = input[key]
                return
            }

            const formattedFlagName = `${key.toString()[0].toUpperCase()}${key.toString().substring(1)}`
            if (Object.keys(flags).includes(`${key.toString()[0].toUpperCase()}${key.toString().substring(1)}`))
                flags[formattedFlagName] = input[key]
        })

        return new ParsedInput(flags.MandatoryArgument, flags, '')
    }
}
