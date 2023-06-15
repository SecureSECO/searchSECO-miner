import yargs from 'yargs'
import { InputParser } from './Input'
import Logger, { Verbosity } from './modules/searchSECO-logger/src/Logger'
import CommandFactory from './CommandFactory'
import DatabaseRequest from './DatabaseRequest'
import Command from './Command'

async function runCommand(command: Command | undefined) {
    try {
        await DatabaseRequest.ConnectToCassandraNode()
        await command?.Execute()
    } catch (e) {
        Logger.Error(`Miner exited with error ${e}. Restarting after 2 seconds...`, Logger.GetCallerLocation())
        setTimeout(async () => {
            await runCommand(command)
        }, 2000)
    }
}

export default class Miner {
    private _id: string

    constructor(id: string) {
        this._id = id
    }

    /**
     * Starts the miner. Essentially does not resolve, as the miner is desinged to run indefinitly
     */
    public async Start() {

        // Sanitize input and setup logger
        const input = InputParser.Parse(yargs.argv)
        Logger.SetModule("miner")
        Logger.SetVerbosity(input.Flags.Verbose || Verbosity.SILENT)
        Logger.Debug("Sanitized and parsed user input", Logger.GetCallerLocation())
    
        const commandFactory = new CommandFactory()
        if (input.Flags.Help)
            commandFactory.PrintHelpMessage(input.Command)
        else if (input.Flags.Version)
            console.log("v1.0.0")
        else {
            // Try to run the command. If an error occurs, restart after 2 seconds.          
            await runCommand(commandFactory.GetCommand(input.Command, this._id, input.Flags))
        }
    }
}
