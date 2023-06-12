# SearchSECO Miner
This is the repository for the SecureSECO DAO miner built to scrape github, upload project data to the SecureSECO database and to connect with the DAO to facilitate claiming of rewards.
## Initial Setup
### Environment variables
All environment variables are listed in `src/config/.env.example`. The variables which are unchanging are already filled in, and the user needs to specify the remaining variables. The variables are exposed via a `.env` file in the same folder as `.env.example`, and this example file serves as a template for the variables that need to be specified in `.env`.
### Setting up environment variables and installing dependencies
#### Variables
Below is a list of the specified environment variables that need to be specified by the user.
- `NODE_ENV`: Either `"development"` or `"production"`. The difference between these two modes can be seen in the way `SIGINT (ctrl+c)` works. In production mode, the current task is finished before the process is exited. In development mode however, the process is killed almost directly.
- `DB_PORT`: The port that the SecureSECO database listens to. The default value is `8003`.
- `DB_HOST`: The IP of the SecureSECO database. The default value is `"131.211.31.209"`.
- `GITHUB_TOKEN`: The github token supplied by the user. Used to fetch author and project data from Github. The github token can have the minimal amount of access rights.
- `PERSONAL_WALLET_ADDRESS`: The wallet address of the user. In order to successfully link to the DAO, the same address must be used as the one linked to the DAO.
#### Dependencies
The miner uses [srcML](https://www.srcml.org/#download) to parse some languages to XML. Install the relevant executable and run `srcml` in a terminal to check whether the installation was successful.
## Installing and running the miner
Download this repository, make a `.env` file, fill in the relevant variables and run the following commands to install the miner:
```
mpn i
git submodule update --init --recursive
```
Then use the following command to run the miner for Windows:
```
npm run start-win
```
For Unix:
```
npm run start-unix
```
When running the start command, the verbosity can be specified by adding `-- -V [verbosity_number]` at the end of the command.
After the start command has been run, the miner will automatically scrape github and upload hashes. The hash count the miner has uploaded can be viewed in the DAO. This is also the place where rewards can be claimed.
#### Verbosity
The miner can be set to be more or less verbose. The specific verbosity values are listed below.
- `1`: Silent. Only `[INFO]` messages are shown
- `2`: Errors only
- `3`: Errors and warnings only
- `4`: Everything
- `5`: Everything including `[DEBUG]` statements
