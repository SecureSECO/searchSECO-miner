/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Command, { StartCommand, CheckCommand, CheckUploadCommand } from './Command';
import { Flags } from './Input';

export default class CommandFactory {
	/**
	 * Prints a help message for a specified command to stdout. If the command does not exist,
	 * a default message will be printed to stdout.
	 * @param cmd The command to print the help message for.
	 */
	public PrintHelpMessage(cmd: string) {
		switch (cmd) {
			case 'start':
				console.log('start:', StartCommand.GetHelpMessage());
				break;
			default:
				console.log('No valid command specified.');
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
			case 'start':
				return new StartCommand(id, flags);
			case 'check':
				return new CheckCommand(id, flags);
			case 'checkupload':
				return new CheckUploadCommand(id, flags);
			default:
				return undefined;
		}
	}
}
