import yargs from 'yargs'
import { InputParser } from './Input'
import Logger from './modules/searchSECO-logger/src/Logger'
import CommandFactory from './CommandFactory'
import EnvironmentDTO from './EnvironmentDTO'

export default class Miner {
    public async Start() {
        const input = InputParser.Parse(yargs.argv)

        Logger.SetModule("miner")
        Logger.SetVerbosity(input.Flags.Verbose)
        Logger.Debug("Sanitized and parsed user input", Logger.GetCallerLocation())
    
        const commandFactory = new CommandFactory()
    
        if (input.Flags.Help)
            commandFactory.PrintHelpMessage(input.Command)
        else if (input.Flags.Version)
            Logger.Info("Versions are not implemented yet", Logger.GetCallerLocation())
        else {
            const env = new EnvironmentDTO()
            const command = commandFactory.GetCommand(input.Command, input.Flags, env)
            await command?.Execute()
        }
    }
}
