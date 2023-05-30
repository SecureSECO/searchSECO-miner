import type { Config } from "@jest/types";

const Config: Config.InitialOptions = {
    verbose: true,
    transform: {
        '^.+\\.tsx?$': 'ts-jest'
    }
}

export default Config