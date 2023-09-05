/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Miner from './Miner';
import { SigInt } from './Command';
import Logger from './modules/searchSECO-logger/src/Logger';
import config from './config/config';
import DatabaseRequest from './DatabaseRequest';
import { v4 as uuidv4 } from 'uuid';

async function createNewMiner(minerId: string) {
	await DatabaseRequest.AddMinerToDatabase(minerId, config.PERSONAL_WALLET_ADDRESS);
	Logger.Info(`New miner with id ${minerId} added to database`, Logger.GetCallerLocation());
}

export default async function start() {
	// Check if a miner associated with the current wallet is idle.
	// If there is, assign the idle miner ID to this miner
	// If it is not, create a new miner

	await DatabaseRequest.TruncateZombieMiners(config.PERSONAL_WALLET_ADDRESS);

	let minerId: string = uuidv4();
	const existingMiners = await DatabaseRequest.ListMinersAssociatedWithWallet(config.PERSONAL_WALLET_ADDRESS);

	if (existingMiners.length > 0) {
		const allRunning = existingMiners.every(({ status }) => status === 'running');
		if (allRunning) createNewMiner(minerId);
		else {
			const { id } = existingMiners.find(({ status }) => status === 'idle');
			minerId = id;
			await DatabaseRequest.SetMinerStatus(id, 'running');
		}
	} else createNewMiner(minerId);

	// Define a custom signal interrupt.
	// When the environment is production, wait until the current process has finished.
	// Else, set the miner to idle and exit immediately.
	process.on('SIGINT', async () => {
		if (config.NODE_ENV === 'development') {
			Logger.Info('Detected signal interrupt, exiting immediately', Logger.GetCallerLocation());
			SigInt.StopProcessImmediately(minerId);
		} else {
			Logger.Info('Detected signal interrupt, finishing current job and exiting', Logger.GetCallerLocation());
			await SigInt.StopProcess(minerId);
		}
	});

	const miner = new Miner(minerId);
	Logger.Info('Starting miner...', Logger.GetCallerLocation());
	await miner.Start();
}

start();
console.timeEnd('start');
