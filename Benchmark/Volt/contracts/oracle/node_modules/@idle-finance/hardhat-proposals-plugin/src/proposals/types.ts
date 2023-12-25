import { BigNumber, BigNumberish, BytesLike, Contract, Signer } from "ethers";
import { Result } from "ethers/lib/utils";
import { EthereumProvider, HardhatRuntimeEnvironment } from "hardhat/types";

export type ContractLike = Contract | string

export type ContractOptional = Contract | null

export interface IAction {
  target: string;
  value: BigNumber;
  signature: string;
  calldata: BytesLike;
}

export interface IProposal {
  simulate(fullSimulation: boolean, force?: boolean): Promise<void>;

  addAction(action: IAction): void;
}

export interface IAlphaProposal extends IProposal {
  contracts: (Contract | null)[];
  args: (Result)[];
}

export interface IProposalBuilder {
  addAction(target: string, value: BigNumberish, signature: string, calldata: BytesLike): IProposalBuilder;
  build(): IProposal
}
