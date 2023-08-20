/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import yargs, { Argv } from 'yargs';
import { Verbosity } from './modules/searchSECO-logger/src/Logger';
import { setCommandInConfig } from './config/config';

export class Flags {
	public MandatoryArgument = '';
	public CPU = 1;
	public Verbose = Verbosity.SILENT;
	public Help = false;
	public Version = false;
	public GithubUser = '';
	public GithubToken = '';
	public Branch = '';
	public WorkerName = '';
	public VulnerabilityCode = '';
	public Lines = '';
	public ProjectCommit = '';
	public Code = '';
	public Commit = '';
}

function checkCommands(yargs: any, argv: any, numRequired: number): boolean {
	if (argv._.length < numRequired) {
		yargs.showHelp()
		return false
	}
	return true
}

export class ParsedInput {
	public Command: string;
	public Flags: Flags;
	public ExecutablePath: string;
	constructor(command: string, flags: Flags, execPath: string) {
		this.Command = command;
		(this.Flags = flags), (this.ExecutablePath = execPath);
	}
}



export class InputParser {
	static Parse(): ParsedInput | undefined {
		const flags = JSON.parse(JSON.stringify(new Flags())) as Flags

		let command: string
		let validCommand = true

		var argv = yargs(process.argv.slice(2))
			.option('verbose', {
				describe: 'set miner verbosity',
				type: 'number',
				alias: 'V'
			})
			.usage('Usage: $0 <command>')
			.command('start', 'starts the miner', () => {
				command = 'start'
			})
			.command('check', 'checks a url against the SearchSECO database', yargs => {
				const argv = yargs
					.usage('usage: $0 check <url> [options]')
					.positional('url', {
						describe: 'The url to check',
						type: 'string',
						demand: true
					})
					.help('help')
					.updateStrings({
						'Commands:': 'item:'
					  })
					.wrap(null)
					.parseSync()
				validCommand = validCommand && checkCommands(yargs, argv, 2)
				if (validCommand) {
					command = 'check'
					flags.MandatoryArgument = argv.url || argv._[1].toString()
				}
			})
			.command('checkupload', 'checks a url against the SearchSECO database and uploads the project', yargs => {
				const argv = yargs
					.usage('usage: $0 checkupload <url> [options]')
					.positional('url', {
						describe: 'The url to check',
						type: 'string',
						demand: true
					})
					.help('help')
					.updateStrings({
						'Commands:': 'item:'
					  })
					.wrap(null)
					.parseSync()
				validCommand = validCommand && checkCommands(yargs, argv, 2)
				if (validCommand) {
					command = 'checkupload'
					flags.MandatoryArgument = argv.url || argv._[1].toString()
				}
			})
			.help('help')
			.wrap(null)
			.parseSync()

		validCommand = validCommand && checkCommands(yargs, argv, 1)
		if (!validCommand)
			return

		setCommandInConfig(command)
		flags.Verbose = argv.verbose || Number(argv._[command === 'start' ? 1 : 2]) || Verbosity.SILENT

		return new ParsedInput(command, flags, '');
	}
}
