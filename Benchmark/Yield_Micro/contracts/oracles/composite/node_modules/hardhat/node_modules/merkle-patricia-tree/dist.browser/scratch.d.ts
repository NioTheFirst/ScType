/// <reference types="node" />
import { DB } from './db';
/**
 * An in-memory wrap over `DB` with an upstream DB
 * which will be queried when a key is not found
 * in the in-memory scratch. This class is used to implement
 * checkpointing functionality in CheckpointTrie.
 */
export declare class ScratchDB extends DB {
    private _upstream;
    constructor(upstreamDB: DB);
    /**
     * Similar to `DB.get`, but first searches in-memory
     * scratch DB, if key not found, searches upstream DB.
     */
    get(key: Buffer): Promise<Buffer | null>;
    copy(): ScratchDB;
}
