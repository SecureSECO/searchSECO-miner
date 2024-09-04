/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Miner from './Miner';
import { SigInt } from './Command';
import Logger, { Verbosity } from './modules/searchSECO-logger/src/Logger';
import config from './config/config';
import DatabaseRequest from './DatabaseRequest';
import { v4 as uuidv4 } from 'uuid';
import { InputParser } from './Input'

async function createNewMiner(minerId: string) {
	if (await DatabaseRequest.AddMinerToDatabase(minerId))
		Logger.Info(`New miner with id ${minerId} added to database`, Logger.GetCallerLocation());
	else Logger.Warning(`Could not add new miner to database`, Logger.GetCallerLocation())
}

async function AssignOrCreateMiner() {
	await DatabaseRequest.ResetInactiveMiners();

	let minerId: string = uuidv4();
	const existingMiners = await DatabaseRequest.ListMinersAssociatedWithWallet();

	if (existingMiners.length > 0) {
		const allRunning = existingMiners.every(({ status }) => status === 'running');
		if (allRunning) await createNewMiner(minerId);
		else {
			const { id } = existingMiners.find(({ status }) => status === 'idle');
			minerId = id;
			Logger.Debug(`Found idle miner: ${minerId}`, Logger.GetCallerLocation())
			await DatabaseRequest.SetMinerStatus(id, 'running');
		}
	} else await createNewMiner(minerId);
	return minerId
}

// Define a custom signal interrupt.
// When the environment is production, wait until the current process has finished.
// Else, set the miner to idle and exit immediately.
function SetCustomSignalInterruptBehaviour(minerId: string) {
	process.on('SIGINT', async () => {
		if (config.NODE_ENV === 'development') {
			Logger.Info('Detected signal interrupt, exiting immediately', Logger.GetCallerLocation());
			SigInt.StopProcessImmediately(minerId);
		} else {
			Logger.Info('Detected signal interrupt, finishing current job and exiting', Logger.GetCallerLocation());
			await SigInt.StopProcess(minerId);
		}
	});
}

export default async function start() {
	const input = InputParser.Parse()
	if (!input)
		return
	Logger.SetModule('start')
	Logger.SetVerbosity(input.Flags.Verbose || Verbosity.SILENT)
	DatabaseRequest.SetVerbosity(input.Flags.Verbose || Verbosity.SILENT)

	Logger.Debug('Sanitized and parsed user input', Logger.GetCallerLocation());
	const minerId = await AssignOrCreateMiner()

	SetCustomSignalInterruptBehaviour(minerId)

	const miner = new Miner(minerId, input.Command, input.Flags);
	Logger.Info('Starting miner...', Logger.GetCallerLocation());
	await miner.Start();
}

start();

