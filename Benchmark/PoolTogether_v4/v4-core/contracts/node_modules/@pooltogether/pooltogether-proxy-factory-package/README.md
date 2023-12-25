# pooltogether-proxy-factory-package

Typescript wrapper to use PoolTogether's Generic Minimal Proxy Factory for deploying contracts.

## How it works

Import this package into your repo using:
`yarn add -D @pooltogether/pooltogether-proxy-factory-package`


Import in the deployments script:
```typescript
import { factoryDeploy } from "@pooltogether/pooltogether-proxy-factory-package"
```
or
```javascript
const { factoryDeploy } = require("@pooltogether/pooltogether-proxy-factory-package")
```


Pass the paramaters required:
```typescript
interface DeploySettings {
    implementationAddress: string
    contractName: string
    overWrite?: boolean
    signer?: any 
    initializeData?: any
    provider: any 
}
```



# Installation
Install the repo and dependencies by running:
`yarn`


# Testing
Run the unit tests locally with:
`yarn test`

## Coverage
Generate the test coverage report with:
`yarn coverage`

Todo:
- use peerDependency for pooltgoether-proxy-factory
- Write script that extracts deployed generic proxy factory addresses automatically
- update tpes for DeploySettings interface
- do we need both the signer and the provider
- prublish non beta version