/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Flags, InputParser } from './Input';
import Logger, { Verbosity } from './modules/searchSECO-logger/src/Logger';
import CommandFactory from './CommandFactory';
import Command, { SigInt } from './Command';
import config from './config/config'

function CheckGithubTokenPresent() {
	return config.GITHUB_TOKEN !== ''
}

/**
 * Try to run a command. If an error orccured, print it to stdout and retry.
 * @param command The command to run
 */
async function Run(command: Command | undefined) {
	try {
		await RunWithoutErrorHandling(command)
	} catch (e) {
		Logger.Error(`Miner exited with error ${e}. Restarting after 2 seconds...`, Logger.GetCallerLocation());
		setTimeout(async () => {
			await Run(command);
		}, 2000);
	}
}

async function RunWithoutErrorHandling(command: Command | undefined) {
	await command?.Execute(Logger.GetVerbosity());
}

export default class Miner {
	private _id: string;
	private _flags: Flags
	private _command: string

	constructor(id: string, command: string, flags: Flags) {
		this._id = id;
		this._flags = flags
		this._command = command
	}

	/**
	 * Starts the miner with the command supplied by the user.
	 */
	public async Start() {
		Logger.SetModule('miner');
		Logger.SetVerbosity(this._flags.Verbose || Verbosity.SILENT);

		if (!CheckGithubTokenPresent()) {
			const isPackage = (process as any).pkg ? true : false
			const message = isPackage 
				? 'Please set one by using the --github_token flag or by building the application from source with a token set in the .env file.'
				: 'Please set a token in the .env file.'
			Logger.Error(`Github token not specified. ${message}`, Logger.GetCallerLocation())
			return
		}

		const commandFactory = new CommandFactory();
		// Try to run the command
		if (config.NODE_ENV == 'development')
			await RunWithoutErrorHandling(commandFactory.GetCommand(this._command, this._id, this._flags));
		else await Run(commandFactory.GetCommand(this._command, this._id, this._flags));
	}
}
