/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import path from 'path';
import dotenv from 'dotenv';

dotenv.config({ path: path.join(__dirname, '../config/.env') });

interface ENV {
	NODE_ENV: string | undefined;
	DB_PORT: string | number | undefined;
	DB_HOST: string | undefined;
	PERSONAL_WALLET_ADDRESS: `0x${string}` | undefined;
	GITHUB_TOKEN: string | undefined;
}

interface Config {
	NODE_ENV: string | undefined;
	DB_PORT: string | number | undefined;
	DB_HOST: string | undefined;
	PERSONAL_WALLET_ADDRESS: `0x${string}` | undefined;
	GITHUB_TOKEN: string | undefined;
}

function getConfig(): ENV {
	return {
		NODE_ENV: process.env.NODE_ENV,
		DB_PORT: process.env.DB_PORT,
		DB_HOST: process.env.DB_HOST,
		PERSONAL_WALLET_ADDRESS: process.env.PERSONAL_WALLET_ADDRESS as `0x${string}`,
		GITHUB_TOKEN: process.env.GITHUB_TOKEN,
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
