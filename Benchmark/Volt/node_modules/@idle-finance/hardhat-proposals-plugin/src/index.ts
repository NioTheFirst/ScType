import { extendEnvironment , extendConfig, task, types } from "hardhat/config";
import { lazyObject } from "hardhat/plugins";
import { HardhatConfig, HardhatUserConfig } from "hardhat/types";

import { AlphaProposal, AlphaProposalBuilder } from "./proposals/compound-alpha";
// import { ExampleHardhatRuntimeEnvironmentField } from "./ExampleHardhatRuntimeEnvironmentField";
// This import is needed to let the TypeScript compiler know that it should include your type
// extensions in your npm package's types file.
import "./type-extensions";
import { GovernorAlpha__factory, VotingToken__factory } from "./ethers-contracts/index"

extendConfig(
  (config: HardhatConfig, userConfig: Readonly<HardhatUserConfig>) => {
    // We apply our default config here. Any other kind of config resolution
    // or normalization should be placed here.
    //
    // `config` is the resolved config, which will be used during runtime and
    // you should modify.
    // `userConfig` is the config as provided by the user. You should not modify
    // it.
    //
    // If you extended the `HardhatConfig` type, you need to make sure that
    // executing this function ensures that the `config` object is in a valid
    // state for its type, including its extentions. For example, you may
    // need to apply a default value, like in this example.
    const userGovernor = userConfig.proposals?.governor
    const userVotingToken = userConfig.proposals?.votingToken

    config.proposals = {
      governor: userGovernor ? userGovernor : "",
      votingToken: userVotingToken ? userVotingToken : ""
    }
  }
);

task("proposal", "Interact with proposals using hardhat")
  .addParam("action", "What type of action to perform from options (info) (default: \"info\")", "info", types.string)
  .addOptionalParam("governor", "The governor address", undefined, types.string)
  .addOptionalParam("votingToken", "The voting token registered with the governor", undefined, types.string)
  .addPositionalParam("id", "The proposal id", undefined,  types.int)
  .setAction(async (args, hre) => {
    const {action, governor, votingToken, id} = args
    
    const governorContract = GovernorAlpha__factory.connect(governor || hre.config.proposals.governor, hre.ethers.provider)
    const votingTokenContract = VotingToken__factory.connect(votingToken || hre.config.proposals.votingToken, hre.ethers.provider)

    switch (action) {
      case "info":
        {
          let proposal = hre.proposals.proposals.alpha()

          proposal.setGovernor(governorContract)
          proposal.setVotingToken(votingTokenContract)
          
          let loadedProposal = await proposal.loadProposal(id)
          await loadedProposal.printProposalInfo()
        }
        break;
    }
  })
  

extendEnvironment((hre) => {
  // We add a field to the Hardhat Runtime Environment here.
  // We use lazyObject to avoid initializing things until they are actually
  // needed.
  hre.proposals = lazyObject(() => {
    return {
      builders: {
        alpha: () => new AlphaProposalBuilder(hre, hre.config.proposals.governor, hre.config.proposals.votingToken)
      },
      proposals: {
        alpha: () => new AlphaProposal(hre)
      }
    }
  });
});
