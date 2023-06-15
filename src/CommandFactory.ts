import Command, { StartCommand } from "./Command";
import { Flags } from "./Input";

export default class CommandFactory {
    /**
     * Prints a help message for a specified command to stdout. If the command does not exist,
     * a default message will be printed to stdout.
     * @param cmd The command to print the help message for.
     */
    public PrintHelpMessage(cmd: string) {
        switch (cmd) {
            case "start": console.log("start:", StartCommand.GetHelpMessage()); break
            default: console.log("No valid command specified.")
        }
    }

    /**
     * Makes a command object based on a command string. When the specified command is
     * not supported, undefined is returned.
     * @param cmd The command string to get the actual command object for
     * @param id The current miner ID
     * @param flags The sanitized flags provided by the user
     * @returns a Command object representing the specified command.
     */
    public GetCommand(cmd: string, id: string, flags: Flags): Command | undefined {
        switch (cmd) {
            case "start": return new StartCommand(id, flags)
            default: return undefined
        }
    }
}