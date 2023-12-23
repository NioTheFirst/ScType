/*
 * Copyright 2019-2020, Offchain Labs, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var ProviderBridge = require('./ethers-web3-bridge')


// wrapProvider was inspired by https://github.com/ethereum-optimism/optimism-monorepo/blob/master/packages/ovm-truffle-provider-wrapper/index.ts
function wrapProvider(provider) {
  if (typeof provider !== 'object' || !provider['sendAsync']) {
    throw Error(
      'Invalid provider. Expected provider to conform to Truffle provider interface!'
    )
  }

  let chainId = 'not set';
	provider.sendAsync({
      jsonrpc: "2.0",
      method: "net_version",
      params: [],
      id: 0
    }, (err, network) => {
	  if (chainId == 'not set') {
	    if (err) {
	      throw Error("couldn't get chain id", err)
	    }
	    if (typeof(network.result) === 'string') {
	    	network.result = parseInt(network.result)
	    }
	    chainId = network.result
	  }
	})
  
  const sendAsync = provider.sendAsync
  const send = provider.send

  provider.sendAsync = function(...args) {
    if (args[0].method === 'eth_sendTransaction') {
      // To properly set chainID for all transactions.
      args[0].params[0].chainId = chainId
    }
    sendAsync.apply(this, args)
  }

  provider.send = function(...args) {
    if (args[0].method === 'eth_sendTransaction') {
      // To properly set chainID for all transactions.
      args[0].params[0].chainId = chainId
    }
    send.apply(this, args)
  }
  return provider
}

module.exports = {
	ProviderBridge,
	wrapProvider
}