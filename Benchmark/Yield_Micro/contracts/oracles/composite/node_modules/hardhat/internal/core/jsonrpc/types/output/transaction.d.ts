/// <reference types="node" />
import * as t from "io-ts";
export declare const rpcAccessList: t.ArrayC<t.TypeC<{
    address: t.Type<Buffer, Buffer, unknown>;
    storageKeys: t.ArrayC<t.Type<Buffer, Buffer, unknown>>;
}>>;
export declare type RpcTransaction = t.TypeOf<typeof rpcTransaction>;
export declare const rpcTransaction: t.TypeC<{
    blockHash: t.Type<Buffer | null, Buffer | null, unknown>;
    blockNumber: t.Type<import("bn.js") | null, import("bn.js") | null, unknown>;
    from: t.Type<Buffer, Buffer, unknown>;
    gas: t.Type<import("bn.js"), import("bn.js"), unknown>;
    gasPrice: t.Type<import("bn.js"), import("bn.js"), unknown>;
    hash: t.Type<Buffer, Buffer, unknown>;
    input: t.Type<Buffer, Buffer, unknown>;
    nonce: t.Type<import("bn.js"), import("bn.js"), unknown>;
    to: t.Type<Buffer | null | undefined, Buffer | null | undefined, unknown>;
    transactionIndex: t.Type<import("bn.js") | null, import("bn.js") | null, unknown>;
    value: t.Type<import("bn.js"), import("bn.js"), unknown>;
    v: t.Type<import("bn.js"), import("bn.js"), unknown>;
    r: t.Type<import("bn.js"), import("bn.js"), unknown>;
    s: t.Type<import("bn.js"), import("bn.js"), unknown>;
    type: t.Type<import("bn.js") | undefined, import("bn.js") | undefined, unknown>;
    chainId: t.Type<import("bn.js") | null | undefined, import("bn.js") | null | undefined, unknown>;
    accessList: t.Type<{
        address: Buffer;
        storageKeys: Buffer[];
    }[] | undefined, {
        address: Buffer;
        storageKeys: Buffer[];
    }[] | undefined, unknown>;
}>;
//# sourceMappingURL=transaction.d.ts.map