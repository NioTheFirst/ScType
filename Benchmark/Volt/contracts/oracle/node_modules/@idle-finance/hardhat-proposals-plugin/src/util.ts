import { BigNumber } from "ethers";
import { JsonRpcProvider } from "@ethersproject/providers";


export function toBigNumber(x: any): BigNumber {return BigNumber.from(x.toString())}
