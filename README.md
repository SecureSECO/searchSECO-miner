# SearchSECO Miner
This is the repository for the SecureSECO DAO miner built to scrape Github, upload project data to the SecureSECO database and to connect with the DAO to facilitate claiming of rewards.
## Initial Setup
This project uses Node v18.
### Environment variables
All environment variables are listed in `src/config/.env.example`. The variables are exposed via a `.env` file in the same folder as `.env.example`, and this example file serves as a template for the variables that need to be specified in `.env`.
### Setting up environment variables and installing dependencies
#### Variables
Below is a list of the specified environment variables that need to be specified by the user.
- `MINER_NAME`: The optional name of the miner. This value defaults to `'client'`
- `GITHUB_TOKEN`: The github token supplied by the user. Used to fetch author and project data from Github. The github token can have the minimal amount of access rights.
- `PERSONAL_WALLET_ADDRESS`: The wallet address of the user. In order to successfully link to the DAO, the same address must be used as the one linked to the DAO.
#### Dependencies
- The miner uses [srcML](https://www.srcml.org/#home) to parse some languages to XML. Install the [relevant executable](https://www.srcml.org/#download). If not installed, the miner will skip all files which have to be parsed with srcml.
- The miner also uses [Git](https://git-scm.com/) to interface with github. Make sure it is installed and run the following commands in a terminal with admin rights:
  - `git config --system core.longpaths true` - Some filenames are too long to be accessed with git, and this flag enables long filenames.
  - `git config --system core.protectNTFS false` - Some filepaths are incorrectly formatted (e.g have symbols such as `:` or `*` in them) for NTFS filesystems, and this flag disables a check for those filepaths.
## Installing and running the miner
### Run using `npm`
Fill in the relevant variables in the `.env` file and install dependencies:
```
npm i
```
Build the miner for the target operating sytem:
```
npm run build-win
```
or
```
npm run build-unix
```
Run the miner with the following command structure:
```
npm run execute -- <command> [options]
```
To get a list of all commands and options, run:
```
npm run execute -- --help
```
### Run using a standalone executable
#### Latest release
Download the latest release and run the miner using the following command:
```
miner <command> [options]
```
The following options have to be set when running from the latest release:
```
--github_token, -g [YOUR_GITHUB_TOKEN]
```
#### Build from source
Optionally fill in all relevant variables in `.env` and run the following command. Choose the target depending on your operating system.
```
npm run package-[win|linux|mac]
```
This will create a folder called `./build`, in which is the executable. This executable can be run the same way as in the latest release, but the `github_token` option does not have to be set if the `.env` file has been created and filled in.


## Verbosity
The miner can be set to be more or less verbose. Each command can be suffixed with a `--verbose [VERBOSITY]` flag. The specific verbosity values are listed below.
- `1`: Silent. Only `[INFO]` messages are shown
- `2`: Errors only
- `3`: Errors and warnings only
- `4`: Everything
- `5`: Everything including `[DEBUG]` statements


## License

This project is licensed under the MIT license. See [LICENSE](/LICENSE) for more info.

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course. © Copyright Utrecht University
(Department of Information and Computing Sciences)
