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
	NODE_ENV: string;
	DB_PORT: string | number;
	DB_HOST: string;
	PERSONAL_WALLET_ADDRESS: string;
	GITHUB_TOKEN: string;
	COMMAND: string;
	MINER_NAME: string
	IS_EXECUTABLE: boolean
}

interface Config {
	NODE_ENV: string;
	DB_PORT: string | number;
	DB_HOST: string;
	PERSONAL_WALLET_ADDRESS: string;
	GITHUB_TOKEN: string;
	COMMAND: string;
	MINER_NAME: string
	IS_EXECUTABLE: boolean
}

function getConfig(): ENV {
	return {
		NODE_ENV: process.env.NODE_ENV || 'production',
		DB_PORT: 8003,
		DB_HOST: '131.211.31.209',
		PERSONAL_WALLET_ADDRESS: process.env.PERSONAL_WALLET_ADDRESS || '',
		GITHUB_TOKEN: process.env.GITHUB_TOKEN || '',
		COMMAND: '',
		MINER_NAME: process.env.MINER_NAME || 'client',
		IS_EXECUTABLE: (process as any).pkg ? true : false
	};
}

export const NullableKeys = [
	'COMMAND',
	'GITHUB_TOKEN',
	'PERSONAL_WALLET_ADDRESS'
] as const

function getSanitizedConfig(config: ENV): Config {
	for (const [key, value] of Object.entries(config))
		if (value === undefined && !NullableKeys.find(validKey => validKey == key)) 
			throw new Error(`Missing non-nullable key ${key} in .env`);
	return config as Config;
}

const config = getConfig();
const sanitizedConfig = getSanitizedConfig(config);
export default sanitizedConfig;

type SettableKey =
	  'COMMAND'
	| 'GITHUB_TOKEN'
	| 'MINER_NAME'
	| 'PERSONAL_WALLET_ADDRESS'


/**
 * Sets a config key with the newly supplied value. Some keys are not settable.
 * @param key The key to set the new value for
 * @param value The value to set
 * @returns `true` when the value has successfully been set, else `false`
 */
export function setInConfig(key: SettableKey, value: typeof sanitizedConfig[keyof Config]): boolean {
	if (typeof value !== typeof sanitizedConfig[key as keyof typeof sanitizedConfig])
		return false

	if (typeof value !== typeof sanitizedConfig[key])
		return false

	sanitizedConfig[key] = value as typeof sanitizedConfig[typeof key]
	return true
}
