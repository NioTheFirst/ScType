import { BigNumberish, BigNumber, BytesLike, Signer } from "ethers";
import { HardhatPluginError } from "hardhat/plugins";
import { HardhatRuntimeEnvironment } from "hardhat/types";

import { toBigNumber } from "../util";
import { IProposal, IAction, IProposalBuilder } from "./types";
import { PACKAGE_NAME, errors } from "../constants";

/**
 * This is an internal state of the proposal which is used to keep track of a proposal.
 */
export enum InternalProposalState {
  UNSUBMITTED,
  SIMULATED,
  SUBMITTED
}

/**
 * Abstract implementation of a proposal
 * 
 * This implementation only contains a subset of the actions required for a proposal
 */
export abstract class Proposal implements IProposal {
  protected readonly hre: HardhatRuntimeEnvironment;
  protected internalState: InternalProposalState;
  
  proposer?: Signer;

  targets: string[]      = []
  values: BigNumber[]    = []
  signatures: string[]   = []
  calldatas: BytesLike[] = []

  constructor(hre: HardhatRuntimeEnvironment) {
    this.hre = hre;

    this.internalState = InternalProposalState.UNSUBMITTED;
  }

  protected markAsSubmitted() {
    this.internalState = InternalProposalState.SUBMITTED
  }

  /**
   * Run a simulation of the proposal
   * 
   * This method will not update the propsal id.
   * 
   * If the proposal has already been simulated, an exception will be thrown to the called.
   * This can be disabled by using the flag `simulate(force=true)`
   *
   * Each proposal type will have its own implmenentation for simulating the proposal,
   * therefore refer to the relavent proposal for details on how the simulate method method works.
   * 
   * There may be some nuance the the implementation to pay attention to in particular.
   * 
   * For example
   *  - Each action may be exected as distinct transactions instead of one
   *  - The timestamps for each action may be slightly different.
   *  - The gas costs from this method should not be relied upon for executing a proposal.
   * 
   * If you want a more accurate (but significantly slower) simulation of the proposal
   * run this method with the flag `simulate(fullSimulation=true)`
   * 
   * @param fullSimulation  Whether to run a full simulation of the proposal (default: false)
   * @param force  Re-execute the proposal even if it has already been simulated before (default: false)
   */
  async simulate(fullSimulation: boolean = false, force?: boolean) {
    if (this.internalState != InternalProposalState.UNSUBMITTED && !force) {
      throw new HardhatPluginError(PACKAGE_NAME, errors.ALREADY_SIMULATED);
    }
    
    if (fullSimulation) await this._fullSimulate();
    else await this._simulate();

    this.internalState = InternalProposalState.SIMULATED
  }

  /**
   * Implementation for running a proposal simulation.
   */
  protected abstract _simulate(): Promise<void>;

  /**
   * Implenentation for running a full proposal simulation
   */
  protected abstract _fullSimulate(): Promise<void>;

  addAction(action: IAction): void {
    this.targets.push(action.target)
    this.values.push(BigNumber.from(action.value))
    this.signatures.push(action.signature)
    this.calldatas.push(action.calldata)
  }

  /**
   * Fetch a proposal from the block chain and return that new proposal
   * 
   * @param data Any data required to load the proposal. Determined by the implementation
   */
  abstract loadProposal(data: any): Promise<Proposal>

  protected getProvider() {return this.hre.network.provider}
  protected getEthersProvider() {return this.hre.ethers.provider}

  protected async mineBlocks(blocks: any) {
    let blocksToMine = toBigNumber(blocks).toNumber()
  
    for (let i = 0; i < blocksToMine; i++) {
      await this.mineBlock()
    }
  }
  
  protected async  mineBlock(timestamp?: number) {
    let provider = this.getEthersProvider()

    if (timestamp) {
      await provider.send("evm_mine", [timestamp])
    } else {
      await provider.send("evm_mine", [])
    }
  }
}

export abstract class ProposalBuilder implements IProposalBuilder {
  private readonly hre: HardhatRuntimeEnvironment;
  abstract proposal: Proposal

  constructor(hre: HardhatRuntimeEnvironment) {
    this.hre = hre
  }
  /**
   * Build and return the proposal
   * 
   * @returns  The built proposal
   */
  abstract build(): Proposal;

  /**
   * Add an action to the proposal
   * 
   * @param target  Target contract address
   * @param value  tx value to send
   * @param signature  Contract function signature to call
   * @param calldata  Call data to pass to function
   */
  abstract addAction(target: string, value: BigNumberish, signature: string, calldata: BytesLike): ProposalBuilder
}
