import Miner from './Miner'
import { SigInt } from './Command'
import Logger from './modules/searchSECO-logger/src/Logger'
import config from './config/config'
import DatabaseRequest from './DatabaseRequest'
import Cache from './Cache'
import { v4 as uuidv4 } from 'uuid'

(async () => {

    let minerId: string = uuidv4()

    async function createNewMiner() {
        await DatabaseRequest.AddMinerToDatabase(minerId)
        Cache.SetMinerId(minerId, 'running')
        Logger.Info(`New miner with id ${minerId} added to database`, Logger.GetCallerLocation())
    }

    Cache.ReadCache()

    
    if (Cache.Store) {
        const allRunning = Object.keys(Cache.Store).reduce((isRunning, currId) => {
            const currentRunning = Cache.Store[currId].status === 'running'
            if (!currentRunning)
                minerId = currId
            return isRunning && currentRunning
        }, true)

        if (allRunning) createNewMiner()
        else {
            await DatabaseRequest.SetMinerStatus(minerId, 'running')
            Cache.SetMinerStatus(minerId, 'running')
        }
    }
    else createNewMiner()

    process.on('SIGINT', async () => {
        if (config.NODE_ENV === "development") {
            Logger.Info("Detected signal interrupt, exiting immediately", Logger.GetCallerLocation())
            await DatabaseRequest.SetMinerStatus(minerId, 'idle')
            Cache.SetMinerStatus(minerId, 'idle')
            process.exit(0)
        } else {
            Logger.Info("Detected signal interrupt, finishing current job and exiting", Logger.GetCallerLocation())
            SigInt.StopProcess().then(async () => {
                await DatabaseRequest.SetMinerStatus(minerId, 'idle')
                Cache.SetMinerStatus(minerId, 'idle')
                process.exit(0)
            })
        }
    })

    const miner = new Miner(minerId)
    Logger.Info("Starting miner...", Logger.GetCallerLocation())
    miner.Start()
})()