import Miner from './Miner'
import { SigInt } from './Command'
import { spawn } from 'child_process'
import Logger from './modules/searchSECO-logger/src/Logger'

(() => {
    process.on('SIGINT', () => {
        Logger.Info("Detected signal interrupt, finishing current job and exiting", Logger.GetCallerLocation())
        SigInt.StopProcess().then(() => process.exit(0))
    })

    const miner = new Miner()
    miner.Start()
})()