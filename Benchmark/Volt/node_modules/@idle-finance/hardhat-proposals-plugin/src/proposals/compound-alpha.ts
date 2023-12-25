import { BigNumber, BytesLike, Contract, Signer, utils, ContractReceipt, ContractTransaction, BigNumberish } from "ethers";
import { FormatTypes, FunctionFragment, hexDataSlice } from "ethers/lib/utils";
import { Provider } from "@ethersproject/providers";
import { Result, defaultAbiCoder } from "ethers/lib/utils";
import { HardhatRuntimeEnvironment } from "hardhat/types";
import { HardhatPluginError } from "hardhat/plugins";

import { GovernorAlpha, GovernorAlpha__factory, VotingToken, VotingToken__factory } from "../ethers-contracts/index"
import { Timelock__factory } from "../ethers-contracts/factories/Timelock__factory";

import { PACKAGE_NAME, errors } from "../constants"
import { InternalProposalState, Proposal, ProposalBuilder } from "./proposal"
import { ContractLike, ContractOptional, IAction } from "./types"
import { toBigNumber } from "../util"

// ---------- Helper Functions ----------

function loadGovernor(contract: ContractLike, provider: Provider) : GovernorAlpha {
  // If `contract` is already a type contract
  if (contract instanceof Contract) {
    return contract as GovernorAlpha
  }
  return GovernorAlpha__factory.connect(contract, provider)
}

function loadVotingToken(contract: ContractLike, provider: Provider) : VotingToken {
  // If `contract` is already a type contract
  if (contract instanceof Contract) {
    return contract as VotingToken
  }
  return VotingToken__factory.connect(contract, provider)
}

// -------------------- Define proposal states --------------------

export enum AlphaProposalState {
  PENDING,
  ACTIVE,
  CANCELED,
  DEFEATED,
  SUCCEDED,
  QUEUED,
  EXPIRED,
  EXECUTED,
}

// -------------------- Define proposal actions --------------------

export interface IAlphaProposalAction extends IAction {
  contract: ContractOptional
  args: Result
}

// -------------------- Define proposal --------------------

export class AlphaProposal extends Proposal {
  state: AlphaProposalState = AlphaProposalState.PENDING
  
  votingToken?: VotingToken;
  governor?: GovernorAlpha;
  
  proposer?: Signer;
  id: BigNumber = BigNumber.from("0");
  description: string = "";
  
  contracts: ContractOptional[] = []
  args: Result[] = []
  
  constructor(hre: HardhatRuntimeEnvironment, governor?: ContractLike, votingToken?: ContractLike) {
    super(hre) // call constructor on Proposal

    this.governor = governor ? loadGovernor(governor, this.getEthersProvider()) : undefined
    this.votingToken = votingToken ? loadVotingToken(votingToken, this.getEthersProvider()) : undefined
  }

  addAction(action: IAlphaProposalAction) {
    super.addAction(action)

    this.contracts.push(action.contract)
    this.args.push(action.args)
  }

  setProposer(proposer: Signer) {this.proposer = proposer}

  setGovernor(governor: ContractLike) {this.governor = loadGovernor(governor, this.getEthersProvider())}
  setVotingToken(votingToken: ContractLike) {
    this.votingToken = loadVotingToken(votingToken, this.getEthersProvider())
  }

  public async propose(proposer?: Signer) {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)

    proposer = proposer ? proposer : this.proposer
    if (!proposer) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_PROPOSER);

    const governorAsProposer = this.governor.connect(proposer)

    const proposalId = await governorAsProposer
      .callStatic
      .propose(this.targets, this.values, this.signatures, this.calldatas, this.description);

    await governorAsProposer.propose(
      this.targets,
      this.values,
      this.signatures,
      this.calldatas,
      this.description)

    this.id = proposalId;

    this.markAsSubmitted()
  }

  public async loadProposal(data: BigNumberish): Promise<AlphaProposal> {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)
    if (!this.votingToken) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_VOTING_TOKEN)
  
    let id = data;
    let proposal = new AlphaProposal(this.hre, this.governor, this.votingToken)
    proposal.markAsSubmitted()

    proposal.id = BigNumber.from(id);
    let proposalInfo = await this.governor.proposals(id)
    let actionsInfo = await this.governor.getActions(id)

    proposal.proposer = new this.hre.ethers.VoidSigner(proposalInfo.proposer)
    proposal.targets = actionsInfo.targets
    proposal.values = actionsInfo[1] // `values` gets overwrittn by array.values
    proposal.signatures = actionsInfo.signatures
    proposal.calldatas = actionsInfo.calldatas

    proposal.description = "<DESCRIPTION NOT LOADED>"
    
    let args = []
    
    for (let i = 0; i < proposal.targets.length; i++) {
      proposal.contracts.push(null) // push null to contracts. 
      const signature = proposal.signatures[i];
      const calldata = proposal.calldatas[i];

      const arg = defaultAbiCoder.decode([ signature ], calldata);
      args.push(arg)
    }
    
    proposal.args = args

    return proposal
  }

  private async getProposalState(): Promise<AlphaProposalState> {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)
    if (this.internalState != InternalProposalState.SUBMITTED) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.PROPOSAL_NOT_SUBMITTED)
    }
    const proposalState = await this.governor.state(this.id)

    return proposalState as AlphaProposalState
  }

  public async vote(signer: Signer, support: boolean=true) {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)

    if (this.internalState != InternalProposalState.SUBMITTED) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.PROPOSAL_NOT_SUBMITTED)
    }

    let currentState = await this.getProposalState()
    if (currentState == AlphaProposalState.ACTIVE) {
      await this.governor.connect(signer).castVote(this.id, support)
    } else {
      throw new HardhatPluginError(PACKAGE_NAME, `Proposal is not in an active state, received ${currentState}`)
    }
  }

  public async queue(signer?: Signer) {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)

    if (this.internalState != InternalProposalState.SUBMITTED) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.PROPOSAL_NOT_SUBMITTED)
    }

    signer = signer ? signer : this.proposer
    if (!signer) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_SIGNER);

    await this.governor.connect(signer).queue(this.id)
  }

  public async execute(signer?: Signer) {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)

    if (this.internalState != InternalProposalState.SUBMITTED) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.PROPOSAL_NOT_SUBMITTED)
    }

    signer = signer ? signer : this.proposer
    if (!signer) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_SIGNER);

    await this.governor.connect(signer).execute(this.id)
  }

  /**
   * This method will simulate the proposal using the full on-chain process.
   * This may take significant time depending on the hardware you are using.
   * 
   * @notice For this method to work the proposal must have a proposer with enough votes to reach quorem
   */
  public async _fullSimulate() {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)
    if (!this.votingToken) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_VOTING_TOKEN)
    if (!this.proposer) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_PROPOSER)

    let provider = this.getEthersProvider()

    let proposerAddress = await this.proposer.getAddress()
    let quoremVotes = await this.governor.quorumVotes();
    let proposerVotes = await this.votingToken.getCurrentVotes(proposerAddress)

    if (proposerVotes < quoremVotes) throw new HardhatPluginError(PACKAGE_NAME, errors.NOT_ENOUGH_VOTES)

    let timelock = Timelock__factory.connect(await this.governor.timelock(), provider)

    await this.propose()
    let votingDelay = await (await this.governor.votingDelay()).add(1)
    await this.mineBlocks(votingDelay)

    await this.vote(this.proposer, true)
    let votingPeriod = await this.governor.votingPeriod()
    await this.mineBlocks(votingPeriod)

    await this.queue()
    let delay = await timelock.delay()
    let blockInfo = await provider.getBlock("latest")
    let endTimeStamp = delay.add(blockInfo.timestamp).add("50").toNumber()
    await this.mineBlock(endTimeStamp)
    
    await this.execute()
  }

  // queues the action to the timelock by impersonating the governor
  // advances time in order to execute proposal
  // analyses errors
  public async _simulate() {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)

    let provider = this.getEthersProvider()
    
    await provider.send("hardhat_impersonateAccount", [this.governor.address])
    await provider.send("hardhat_setBalance", [this.governor.address, "0xffffffffffffffff"])
    let governorSigner = await this.hre.ethers.getSigner(this.governor.address)

    let timelock = Timelock__factory.connect(await this.governor.timelock(), governorSigner)
    
    await provider.send("hardhat_impersonateAccount", [timelock.address])
    await provider.send("hardhat_setBalance", [timelock.address, "0xffffffffffffffff"])
    let timelockSigner = provider.getSigner(timelock.address)
    
    let blockInfo = await provider.getBlock("latest")
    let delay = await timelock.delay()

    let eta = delay.add(blockInfo.timestamp).add("50")

    await provider.send("evm_setAutomine", [false])
    for (let i = 0; i < this.targets.length; i++) {
      await timelock.queueTransaction(this.targets[i], this.values[i], this.signatures[i], this.calldatas[i], eta)
    }
    await this.mineBlocks(1)
    await this.mineBlock(eta.toNumber())

    let receipts = new Array<ContractTransaction>();
    for (let i = 0; i < this.targets.length; i++) {
      await timelock.executeTransaction(this.targets[i], this.values[i], this.signatures[i], this.calldatas[i], eta).then(
        receipt => {receipts.push(receipt)},
        async (timelockError) => {
          // analyse error
          let timelockErrorMessage = timelockError.error.message.match(/^[\w\s:]+'(.*)'$/m)[1]
          let contractErrorMesage

          // call the method on the contract as if it was the timelock
          // this will produce a more relavent message as to the failure of the action
          let contract = await this.contracts[i]?.connect(timelockSigner)
          if (contract) {
            await contract.callStatic[this.signatures[i]](...this.args[i]).catch(contractError => {
              contractErrorMesage = contractError.message.match(/^[\w\s:]+'(.*)'$/m)[1]
            })
          }

          throw new HardhatPluginError(PACKAGE_NAME, 
          `Proposal action ${i} failed.
          Target: ${this.targets[i]}
          Signature: ${this.signatures[i]}
          Args: ${this.args[i]}\n
          Timelock revert message: ${timelockErrorMessage}
          Contract revert message: ${contractErrorMesage}`)
        }
      )
    }

    await this.mineBlock()
    for (let i = 0; i < this.targets.length; i++) {
      let r = await receipts[i].wait().catch(r => {return r.receipt as ContractReceipt})
      if (r.status != 1) {
        throw new HardhatPluginError(PACKAGE_NAME, `Action ${i} failed`)
      }
    }
    await provider.send("evm_setAutomine", [true])
    await provider.send("hardhat_stopImpersonatingAccount", [this.governor.address])
    await provider.send("hardhat_stopImpersonatingAccount", [timelock.address])
  }

  public async printProposalInfo() {
    if (!this.governor) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_GOVERNOR)
    if (!this.votingToken) throw new HardhatPluginError(PACKAGE_NAME, errors.NO_VOTING_TOKEN)
    
    console.log('--------------------------------------------------------')
    if (this.internalState == InternalProposalState.SUBMITTED) {
      const proposalInfo = await this.governor.proposals(this.id)
      const state = await this.getProposalState()
      
      let votingTokenName = await this.votingToken!.name();
      let votingTokenDecimals = BigNumber.from("10").pow(await this.votingToken.decimals());
      
      console.log(`Id: ${this.id.toString()}`)
      console.log(`Description: ${this.description}`)
      console.log(`For Votes: ${proposalInfo.forVotes.div(votingTokenDecimals)} ${votingTokenName} Votes`)
      console.log(`Agasint Votes: ${proposalInfo.againstVotes.div(votingTokenDecimals)} ${votingTokenName} Votes`)

      console.log(`Vote End: ${proposalInfo.endBlock}`)

      console.log(`State: ${state.toString()}`)
    } else {
      console.log("Unsubmitted proposal")
      console.log(`Description: ${this.description}`)
    }


    for (let i = 0; i < this.targets.length; i++) {
      const contract = this.contracts[i]
      const target = this.targets[i]
      const signature = this.signatures[i]
      const value = this.values[i]
      const args = this.args[i]
      
      let name = ""
      if (contract?.functions['name()'] != null) {
        name = (await contract.functions['name()']()).toString()
      }

      console.log(`Action ${i}`)
      if (name == "") {
        console.log(` ├─ target ───── ${target}`)
      }
      else {
        console.log(` ├─ target ───── ${target} (name: ${name})`)
      }
      if (!value.isZero()) {
        console.log(` ├─ value ────── ${utils.formatEther(value.toString())} ETH`)
      }
      console.log(` ├─ signature ── ${signature}`)
      for (let j = 0; j < args.length-1; j++) {
        const arg = args[j];
        console.log(` ├─ args [ ${j} ] ─ ${arg}`)
      }
      console.log(` └─ args [ ${args.length-1} ] ─ ${args[args.length-1]}`)
    }
  }
}

// -------------------- Define proposal builder --------------------

export class AlphaProposalBuilder extends ProposalBuilder {
  maxActions: number;
  proposal: AlphaProposal

  constructor(hre: HardhatRuntimeEnvironment, governor?: ContractLike, votingToken?: ContractLike, maxActions=10) {
    super(hre)

    this.maxActions = maxActions;
    this.proposal = new AlphaProposal(hre, governor, votingToken)
  }
  setGovernor(governor: ContractLike): AlphaProposalBuilder {
    this.proposal.setGovernor(governor)

    return this;
  }

  setVotingToken(votingToken: ContractLike): AlphaProposalBuilder {
    this.proposal.setVotingToken(votingToken)

    return this;
  }


  addAction(target: string, value: BigNumberish, signature: string, calldata: BytesLike): AlphaProposalBuilder {
    if (this.proposal.targets.length >= this.maxActions) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.TOO_MANY_ACTIONS);
    }
    
    value = toBigNumber(value)
    const contract = null
    const args = defaultAbiCoder.decode([ signature ], calldata);

    this.proposal.addAction({target, value, signature, calldata, contract, args})
    return this;
  }

  addContractAction(contract: Contract, method: string, functionArgs: any[], value?: BigNumberish): AlphaProposalBuilder {
    if (this.proposal.targets.length >= this.maxActions) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.TOO_MANY_ACTIONS);
    }

    value = value ? toBigNumber(value) : toBigNumber("0")
    const target = contract.address
    const functionFragment: FunctionFragment = contract.interface.getFunction(method);
    const signature = functionFragment.format(FormatTypes.sighash);

    if (functionFragment.inputs.length != functionArgs.length) {
      throw new HardhatPluginError(PACKAGE_NAME, "arguments length do not match signature")
    }

    // encode function call data
    const functionData = contract.interface.encodeFunctionData(functionFragment, functionArgs);
    const args = contract.interface.decodeFunctionData(
      functionFragment,
      functionData
    );
    const calldata = hexDataSlice(functionData, 4); // Remove the sighash from the function data

    this.proposal.addAction({target, value, signature, calldata, contract, args})
    return this;
  }

  setProposer(proposer: Signer): AlphaProposalBuilder {
    this.proposal.setProposer(proposer)

    return this;
  }

  /**
   * Set the description for the proposal
   * 
   * Some UI interfaces for proposals require a newline `\n`
   * be added in the description to partition the proposal
   * title and the proposal description. It is at the users
   * descresion whether to add this or not. 
   * 
   * @param description  The description field to set for the proposal
   */
  setDescription(description: string): AlphaProposalBuilder {
    this.proposal.description = description;

    return this;
  }

  build() {return this.proposal}
}
