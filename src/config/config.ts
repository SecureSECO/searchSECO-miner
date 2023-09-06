/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import path from 'path';

require('dotenv').config({ path: path.join(__dirname, './.env') });

interface ENV {
	NODE_ENV: string | undefined;
	DB_PORT: string | number | undefined;
	DB_HOST: string | undefined;
	PERSONAL_WALLET_ADDRESS: `0x${string}` | undefined;
	GITHUB_TOKEN: string | undefined;
	COMMAND: string | undefined;
	MINER_NAME: string | undefined
}

interface Config {
	NODE_ENV: string | undefined;
	DB_PORT: string | number | undefined;
	DB_HOST: string | undefined;
	PERSONAL_WALLET_ADDRESS: `0x${string}` | undefined;
	GITHUB_TOKEN: string | undefined;
	COMMAND: string | undefined;
	MINER_NAME: string | undefined
}

function getConfig(): ENV {
	return {
		NODE_ENV: process.env.NODE_ENV,
		DB_PORT: 8003,
		DB_HOST: '131.211.31.209',
		PERSONAL_WALLET_ADDRESS: process.env.PERSONAL_WALLET_ADDRESS as `0x${string}`,
		GITHUB_TOKEN: process.env.GITHUB_TOKEN || '',
		COMMAND: '',
		MINER_NAME: process.env.MINER_NAME || 'client'
	};
}

function getSanitizedConfig(config: ENV): Config {
	for (const [key, value] of Object.entries(config)) {
		if (value === undefined) throw new Error(`Missing key ${key} in .env`);
	}
	return config as Config;
}

const config = getConfig();
const sanitizedConfig = getSanitizedConfig(config);

export default sanitizedConfig;

export function setInConfig(key: any, value: any) {
	if (Object.keys(config).includes(key))
		return
	if (typeof value !== typeof sanitizedConfig[key as keyof typeof config])
		return

	sanitizedConfig[key as keyof typeof config] = value
}
