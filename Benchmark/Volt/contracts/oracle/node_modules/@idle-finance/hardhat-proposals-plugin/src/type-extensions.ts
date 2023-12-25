// If your plugin extends types from another plugin, you should import the plugin here.

// To extend one of Hardhat's types, you need to import the module where it has been defined, and redeclare it.
// import "hardhat/types/config";
import "hardhat/types/runtime";

// import { ExampleHardhatRuntimeEnvironmentField } from "./ExampleHardhatRuntimeEnvironmentField";
import { AlphaProposal, AlphaProposalBuilder } from "./proposals/compound-alpha";

declare module "hardhat/types/config" {
  // This is an example of an extension to one of the Hardhat config values.

  // We extendr the UserConfig type, which represents the config as writen
  // by the users. Things are normally optional here.
  export interface ProposalsUserConfig {
    governor?: string;
    votingToken?: string;
  }

//   // We also extend the Config type, which represents the configuration
//   // after it has been resolved. This is the type used during the execution
//   // of tasks, tests and scripts.
//   // Normally, you don't want things to be optional here. As you can apply
//   // default values using the extendConfig function.
  export interface ProposalsConfig {
    governor: string;
    votingToken: string;
  }

  export interface HardhatUserConfig {
    proposals?: ProposalsUserConfig
  }

  export interface HardhatConfig {
    proposals: ProposalsConfig
  }
}

export interface ProposalsHardHatRunTimeEnvironmentField {
  builders: {
    alpha: () => AlphaProposalBuilder
  }
  proposals: {
    alpha: () => AlphaProposal
  }
}

declare module "hardhat/types/runtime" {
  // This is an example of an extension to the Hardhat Runtime Environment.
  // This new field will be available in tasks' actions, scripts, and tests.
  export interface HardhatRuntimeEnvironment {
    proposals: ProposalsHardHatRunTimeEnvironmentField
  }
}
