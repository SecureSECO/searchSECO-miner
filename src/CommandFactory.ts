import Command, { StartCommand } from "./Command";
import EnvironmentDTO from "./EnvironmentDTO";
import { Flags } from "./Input";

export default class CommandFactory {
    public PrintHelpMessage(cmd: string) {
        switch (cmd) {
            case "start": console.log("start:", StartCommand.GetHelpMessage()); break
            case "list": console.log("list:", "List the claimable tokens"); break
            case "claim": console.log("claim:", "Claim all tokens"); break
        }
    }

    public GetCommand(cmd: string, flags: Flags, env: EnvironmentDTO): Command | undefined {
        switch (cmd) {
            case "start": return new StartCommand(flags, env)
            default: return undefined
        }
    }
}