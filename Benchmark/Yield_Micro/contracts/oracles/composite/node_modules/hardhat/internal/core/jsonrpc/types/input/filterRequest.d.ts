/// <reference types="node" />
import * as t from "io-ts";
export declare const rpcFilterRequest: t.TypeC<{
    fromBlock: t.Type<import("bn.js") | "earliest" | "latest" | "pending" | undefined, import("bn.js") | "earliest" | "latest" | "pending" | undefined, unknown>;
    toBlock: t.Type<import("bn.js") | "earliest" | "latest" | "pending" | undefined, import("bn.js") | "earliest" | "latest" | "pending" | undefined, unknown>;
    address: t.Type<Buffer | Buffer[] | undefined, Buffer | Buffer[] | undefined, unknown>;
    topics: t.Type<(Buffer | (Buffer | null)[] | null)[] | undefined, (Buffer | (Buffer | null)[] | null)[] | undefined, unknown>;
    blockHash: t.Type<Buffer | undefined, Buffer | undefined, unknown>;
}>;
export declare type RpcFilterRequest = t.TypeOf<typeof rpcFilterRequest>;
export declare const optionalRpcFilterRequest: t.Type<{
    fromBlock: import("bn.js") | "earliest" | "latest" | "pending" | undefined;
    toBlock: import("bn.js") | "earliest" | "latest" | "pending" | undefined;
    address: Buffer | Buffer[] | undefined;
    topics: (Buffer | (Buffer | null)[] | null)[] | undefined;
    blockHash: Buffer | undefined;
} | undefined, {
    fromBlock: import("bn.js") | "earliest" | "latest" | "pending" | undefined;
    toBlock: import("bn.js") | "earliest" | "latest" | "pending" | undefined;
    address: Buffer | Buffer[] | undefined;
    topics: (Buffer | (Buffer | null)[] | null)[] | undefined;
    blockHash: Buffer | undefined;
} | undefined, unknown>;
export declare type OptionalRpcFilterRequest = t.TypeOf<typeof optionalRpcFilterRequest>;
//# sourceMappingURL=filterRequest.d.ts.map