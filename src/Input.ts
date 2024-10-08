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
	miner_name?: string;
	github_token?: string;
	wallet_address?: string;
	json_token?: string;
	json_url?: string;
	_: (string | number)[];
	$0: string;
};

export class InputParser {
	static Parse(): ParsedInput | undefined {
		const flags = JSON.parse(JSON.stringify(new Flags())) as Flags;

		let command: string;
		let validCommand = true;

		const parser: Argv<Input> = yargs
			.option('verbose', {
				describe: 'set the miner verbosity. Possible values are 1|2|3|4|5',
				type: 'number',
				alias: 'V',
			})
			.option('branch', {
				type: 'string',
				description: 'The branch to check.',
				alias: 'b',
			})
			.option('tag', {
				type: 'string',
				description: 'The project version to check.',
				alias: 'T',
			})
			.option('threads', {
				type: 'number',
				description: 'How many threads to use during parsing.',
				alias: 't',
			})
			.option('miner_name', {
				type: 'string',
				description: 'Optional name for the miner.',
			})
			.option('github_token', {
				type: 'string',
				description: 'The github token to use for downloading repositories',
				alias: 'g',
			})
			.option('json_token', {
				type: 'string',
				description: 'The json token to use for authenticating in database requests',
			})
			.option('json_url', {
				type: 'string',
				description: 'The url where the json api to the database is located',
				alias: 'u',
			})
			.option('wallet_address', {
				type: 'string',
				description: 'The wallet address used to link the miner to the DAO.',
				alias: 'w',
			})
			.usage('Usage: $0 <command>')
			.command('start', 'starts the miner', (yargs) => {
				command = 'start';
				return yargs;
			})
			.command('check', 'checks a url against the SearchSECO database', (yargs) => {
				command = 'check';
				return yargs
					.usage('usage: $0 check <url> [options]')
					.positional('url', {
						describe: 'The url to check',
						type: 'string',
						demandOption: true,
					})
					.help('help')
					.wrap(null);
			})
			.command('checkupload', 'checks a url against the SearchSECO database and uploads the project', (yargs) => {
				command = 'checkupload';
				return yargs
					.usage('usage: $0 checkupload <url> [options]')
					.positional('url', {
						describe: 'The url to check',
						type: 'string',
						demandOption: true,
					})
					.help('help')
					.wrap(null);
			})
			.help('help')
			.wrap(null);

		let parsed: Input;
		parser.parseSync(process.argv.slice(2), flags, (err, argv) => {
			if (err) validCommand = false;
			parsed = argv;
		});

		if (!command || !validCommand) {
			yargs.showHelp();
			return;
		}

		if (parsed.url || parsed._[1]?.toString()) flags.MandatoryArgument = parsed.url || parsed._[1].toString();
		if (parsed.branch) flags.Branch = parsed.branch;
		if (parsed.tag) flags.ProjectCommit = parsed.tag;
		if (parsed.verbose) flags.Verbose = Number(parsed.verbose);
		if (parsed.threads) flags.Threads = Number(parsed.threads);
		if (parsed.miner_name) setInConfig('MINER_NAME', parsed.miner_name);
		if (parsed.github_token) setInConfig('GITHUB_TOKEN', parsed.github_token);
		if (parsed.wallet_address) setInConfig('PERSONAL_WALLET_ADDRESS', parsed.wallet_address);
		if (parsed.json_token) setInConfig('JSON_TOKEN', parsed.json_token);
		if (parsed.json_url) setInConfig('JSON_URL', parsed.json_url);

		setInConfig('COMMAND', command);

		return new ParsedInput(command, flags, '');
	}
}
