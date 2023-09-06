/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import yargs, { Argv } from 'yargs';
import { Verbosity } from './modules/searchSECO-logger/src/Logger';
import config, { setInConfig } from './config/config';

export class Flags {
	public MandatoryArgument = '';
	public Threads = 4;
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
		yargs.showHelp();
		return false;
	}
	return true;
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

type Input = {
	verbose?: Verbosity;
	url?: string;
	branch?: string;
	tag?: string;
	threads?: number;
	name?: string,
	github_token?: string,
	_: (string | number)[];
	$0: string;
};

export class InputParser {
	static Parse(): ParsedInput | undefined {
		const flags = JSON.parse(JSON.stringify(new Flags())) as Flags;

		let command: string;
		const validCommand = true;

		const argv: Argv<Input> = yargs(process.argv.slice(2))
			.option('verbose', {
				describe: 'set miner verbosity',
				type: 'number',
				alias: 'V',
			})
			.option('branch', {
				type: 'string',
				description: 'The branch to check',
				alias: 'b',
			})
			.option('tag', {
				type: 'string',
				description: 'The project version to check.',
				alias: 'T',
			})
			.option('threads', {
				type: 'number',
				description: 'How many threads to use during parsing',
				alias: 't',
			})
			.option('name', {
				type: 'string',
				description: 'optional name for the miner'
			})
			.option('github_token', {
				type: 'string',
				description: 'The github token to use for downloading repositories',
				alias: 'g'
			})
			.usage('Usage: $0 <command>')
			.command('start', 'starts the miner', () => {
				command = 'start';
			})
			.command('check', 'checks a url against the SearchSECO database', (yargs) => {
				yargs
					.usage('usage: $0 check <url> [options]')
					.positional('url', {
						describe: 'The url to check',
						type: 'string',
						demand: true,
					})
					.help('help')
					.wrap(null);
				command = 'check';
			})
			.command('checkupload', 'checks a url against the SearchSECO database and uploads the project', (yargs) => {
				yargs
					.usage('usage: $0 checkupload <url> [options]')
					.positional('url', {
						describe: 'The url to check',
						type: 'string',
						demand: true,
					})
					.help('help')
					.wrap(null);
				command = 'checkupload';
			})
			.help('help')
			.wrap(null);

		const parsed = argv.parseSync();
		if (!validCommand) return;

		if (parsed.url || parsed._[1]?.toString()) flags.MandatoryArgument = parsed.url || parsed._[1].toString();
		if (parsed.branch) flags.Branch = parsed.branch;
		if (parsed.tag) flags.ProjectCommit = parsed.tag;
		if (parsed.verbose) flags.Verbose = Number(parsed.verbose);
		if (parsed.threads) flags.Threads = Number(parsed.threads);
		if (parsed.name) 
			setInConfig('NAME', parsed.name)
		if (parsed.github_token) setInConfig('GITHUB_TOKEN', parsed.github_token)

		setInConfig('COMMAND', command)

		return new ParsedInput(command, flags, '');
	}
}
