import Miner from './Miner'
import { SigInt } from './Command'
import Logger from './modules/searchSECO-logger/src/Logger'
import config from './config/config'
import DatabaseRequest from './DatabaseRequest'
import { v4 as uuidv4 } from 'uuid'

(async () => {

    await new Promise(resolve => setTimeout(resolve, 3000))

    let minerId: string = uuidv4()

    async function createNewMiner() {
        await DatabaseRequest.AddMinerToDatabase(minerId, config.PERSONAL_WALLET_ADDRESS)
        Logger.Info(`New miner with id ${minerId} added to database`, Logger.GetCallerLocation())
    }

    const miners = await DatabaseRequest.ListMinersAssociatedWithWallet(config.PERSONAL_WALLET_ADDRESS)
    
    if (miners.length > 0) {
        const allRunning = miners.every(({ status }) => status === 'running')
        if (allRunning) createNewMiner()
        else {
            const { id } = miners.find(({ status }) => status === 'idle')
            minerId = id
            await DatabaseRequest.SetMinerStatus(id, 'running')
        }
    }
    else createNewMiner()

    process.on('SIGINT', async () => {
        if (config.NODE_ENV === "development") {
            Logger.Info("Detected signal interrupt, exiting immediately", Logger.GetCallerLocation())
            await DatabaseRequest.SetMinerStatus(minerId, 'idle')
            process.exit(0)
        } else {
            Logger.Info("Detected signal interrupt, finishing current job and exiting", Logger.GetCallerLocation())
            SigInt.StopProcess().then(async () => {
                await DatabaseRequest.SetMinerStatus(minerId, 'idle')
                process.exit(0)
            })
        }
    })

    const miner = new Miner(minerId)
    Logger.Info("Starting miner...", Logger.GetCallerLocation())
    miner.Start()
})()