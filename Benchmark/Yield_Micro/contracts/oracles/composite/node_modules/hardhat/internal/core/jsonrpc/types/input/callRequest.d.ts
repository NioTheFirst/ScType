/// <reference types="node" />
import * as t from "io-ts";
export declare const rpcCallRequest: t.TypeC<{
    from: t.Type<Buffer | undefined, Buffer | undefined, unknown>;
    to: t.Type<Buffer | undefined, Buffer | undefined, unknown>;
    gas: t.Type<import("bn.js") | undefined, import("bn.js") | undefined, unknown>;
    gasPrice: t.Type<import("bn.js") | undefined, import("bn.js") | undefined, unknown>;
    value: t.Type<import("bn.js") | undefined, import("bn.js") | undefined, unknown>;
    data: t.Type<Buffer | undefined, Buffer | undefined, unknown>;
    accessList: t.Type<{
        address: Buffer;
        storageKeys: Buffer[];
    }[] | undefined, {
        address: Buffer;
        storageKeys: Buffer[];
    }[] | undefined, unknown>;
}>;
export declare type RpcCallRequest = t.TypeOf<typeof rpcCallRequest>;
//# sourceMappingURL=callRequest.d.ts.map