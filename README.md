# SecureSECO
The goal of the SecureSECO initiative is to secure and increase trust in the software ecosystem, through the use of distributed ledger technology and empirical software engineering research.

The software ecosystem is a trust-rich part of the world. Collaboratively, software engineers put their trust in major hubs in the ecosystem, such as package managers, repository services, and programming language ecosystems. However, there are many parts of the chain in which this trust can be broken. We present a vision for a trust ensuring mechanism in the software ecosystem that mitigates the presented risks. If our community manages to implement this mechanism, we can create an urgently needed secure software ecosystem.

The initiative is an academic initiative with partners from several universities and companies.

### Website

https://secureseco.org/

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
## Library Dependencies

searchSECO-miner uses the following external libraries and modules:

- **cassandra-driver**: ^4.6.4
- **copyfiles**: ^2.4.1
- **dotenv**: ^16.0.3
- **prompt-sync**: ^4.2.0
- **uuid**: ^9.0.0
- **yargs**: ^17.7.2
- **searchseco-crawler** : "file:src/modules/searchSECO-crawler"
- **searchseco-databaseapi**: "file:src/modules/searchSECO-databaseAPI"
- **searchseco-logger**: "file:src/modules/searchSECO-logger"
- **searchseco-parser**: "file:src/modules/searchSECO-parser"
- **searchseco-spider**: "file:src/modules/searchSECO-spider"
  
## Installing and running the miner
### Run using `npm`
Install submodules:
```
git submodule init 
```
Update the submodules:
```
git submodule update --init --recursive
```
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
For example:
```
npm run execute -- check https://github.com/SecureSECO/searchSECO-miner -V 5
```
For help:
```
npm help run-script
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

## Related Artciles

Jansen, S., Farshidi, S., Gousios, G., Visser, J., Storm, T. V. D., & Bruntink, M. (2020). SearchSECO: A Worldwide Index of the Open Source Software Ecosystem. In M. Papadakis, & M. Cordy (Eds.), Proceedings of the 19th Belgium-Netherlands Software Evolution Workshop, BENEVOL 2020, Luxembourg, December 3-4, 2020 (Vol. 2912). (CEUR Workshop Proceedings). CEUR-WS.org. http://ceurws.org/Vol-2912/./paper3.pdf

Deekshitha, S. Farshidi, J. Maassen, R. Bakhshi, R. Van Nieuwpoort and S. Jansen, "FAIRSECO: An Extensible Framework for Impact Measurement of Research Software," 2023 IEEE 19th International Conference on e-Science (e-Science), Limassol, Cyprus, 2023, pp. 1-10, doi: 10.1109/e-Science58273.2023.10254664. https://ieeexplore.ieee.org/document/10254664


