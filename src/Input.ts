/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import yargs from 'yargs';
import { Verbosity } from './modules/searchSECO-logger/src/Logger';

/**
 * The different flag options
 */
enum FlagName {
	HELP = 'Help',
	VERSION = 'Version',
	VERBOSE = 'Verbose',
	COMMAND = 'Command',
}

/**
 * Maps the short hand flags to their long counterparts
 */
const shorthandToLongMapping: Map<string, FlagName> = new Map<string, FlagName>([
	['h', FlagName.HELP],
	['v', FlagName.VERSION],
	['V', FlagName.VERBOSE],
]);

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
	static Parse(): ParsedInput {
		const flags = JSON.parse(JSON.stringify(new Flags()));

		let command: string
		yargs.option('verbose', {
			describe: 'set miner verbosity',
			type: 'number'
		}).argv

		yargs.command('start', 'starts the miner', () => {
			command = 'start'
		}).argv

		yargs.command('check', 'checks a url against the SecureSECO database', yargs => {
			yargs.positional('url', {
				describe: 'The url to check',
				type: 'string',
				demandOption: true
			})
		}, argv => {
			command = 'check'
			flags.MandatoryArgument = argv._[1]
			flags.Verbose = argv._[2] || Verbosity.SILENT
		}).argv
		
		// Object.keys(argv).forEach((key: keyof typeof argv) => {
		// 	if (key.toString() === '$0') return;

		// 	// // primary argument
		// 	// if (key.toString() === '_') {
		// 	// 	command = argv[key][0]
		// 	// 	flags.MandatoryArgument = (input[key.toString() as keyof typeof argv])[command === 'check' ? 1 : 0];
		// 	// 	return;
		// 	// }

		// 	// if (key.toString().length == 1 && shorthandToLongMapping.has(key.toString())) {
		// 	// 	const flagName = shorthandToLongMapping.get(key.toString());
		// 	// 	flags[flagName] = input[key];
		// 	// 	return;
		// 	// }

		// 	const formattedFlagName = `${key.toString()[0].toUpperCase()}${key.toString().substring(1)}`;
		// 	if (Object.keys(flags).includes(`${key.toString()[0].toUpperCase()}${key.toString().substring(1)}`))
		// 		flags[formattedFlagName] = argv[key];
		// });

		return new ParsedInput(command, flags, '');
	}
}
