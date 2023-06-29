/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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

type UserInput = {
	[key: string]: any;
};

export class InputParser {
	static Parse(input: UserInput): ParsedInput {
		const flags = JSON.parse(JSON.stringify(new Flags()));

		Object.keys(input).forEach((key: keyof UserInput) => {
			if (key.toString() === '$0') return;

			if (key.toString() === '_') {
				flags.MandatoryArgument = (input[key.toString() as keyof UserInput] as string[])[0];
				return;
			}

			if (key.toString().length == 1 && shorthandToLongMapping.has(key.toString())) {
				const flagName = shorthandToLongMapping.get(key.toString());
				flags[flagName] = input[key];
				return;
			}

			const formattedFlagName = `${key.toString()[0].toUpperCase()}${key.toString().substring(1)}`;
			if (Object.keys(flags).includes(`${key.toString()[0].toUpperCase()}${key.toString().substring(1)}`))
				flags[formattedFlagName] = input[key];
		});

		return new ParsedInput(flags.MandatoryArgument, flags, '');
	}
}
