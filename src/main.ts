import Miner from './Miner'
import { SigInt } from './Command'
import Logger from './modules/searchSECO-logger/src/Logger'
import config from './config/config'
import DatabaseRequest from './DatabaseRequest'

(() => {
    process.on('SIGINT', async () => {
        if (config.NODE_ENV === "development") {
            Logger.Info("Detected signal interrupt, exiting immediately", Logger.GetCallerLocation())
            await DatabaseRequest.SetMinerStatus('idle')
            process.exit(0)
        } else {
            Logger.Info("Detected signal interrupt, finishing current job and exiting", Logger.GetCallerLocation())
            SigInt.StopProcess().then(async () => {
                await DatabaseRequest.SetMinerStatus('idle')
                process.exit(0)
            })
        }
    })

    const miner = new Miner()
    miner.Start()
})()