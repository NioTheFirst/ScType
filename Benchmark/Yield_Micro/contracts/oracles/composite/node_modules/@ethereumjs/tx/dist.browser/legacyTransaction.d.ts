/// <reference types="node" />
import { TxOptions, TxData, JsonTx } from './types';
import { BaseTransaction } from './baseTransaction';
/**
 * An Ethereum non-typed (legacy) transaction
 */
export default class Transaction extends BaseTransaction<Transaction> {
    /**
     * Instantiate a transaction from a data dictionary
     */
    static fromTxData(txData: TxData, opts?: TxOptions): Transaction;
    /**
     * Instantiate a transaction from the serialized tx.
     */
    static fromSerializedTx(serialized: Buffer, opts?: TxOptions): Transaction;
    /**
     * Instantiate a transaction from the serialized tx.
     * (alias of `fromSerializedTx()`)
     *
     * @deprecated this constructor alias is deprecated and will be removed
     * in favor of the `fromSerializedTx()` constructor
     */
    static fromRlpSerializedTx(serialized: Buffer, opts?: TxOptions): Transaction;
    /**
     * Create a transaction from a values array.
     *
     * The format is:
     * nonce, gasPrice, gasLimit, to, value, data, v, r, s
     */
    static fromValuesArray(values: Buffer[], opts?: TxOptions): Transaction;
    /**
     * This constructor takes the values, validates them, assigns them and freezes the object.
     *
     * It is not recommended to use this constructor directly. Instead use
     * the static factory methods to assist in creating a Transaction object from
     * varying data types.
     */
    constructor(txData: TxData, opts?: TxOptions);
    /**
     * Returns a Buffer Array of the raw Buffers of this transaction, in order.
     */
    raw(): Buffer[];
    /**
     * Returns the rlp encoding of the transaction.
     */
    serialize(): Buffer;
    private _unsignedTxImplementsEIP155;
    private _getMessageToSign;
    /**
     * Computes a sha3-256 hash of the serialized unsigned tx, which is used to sign the transaction.
     */
    getMessageToSign(): Buffer;
    /**
     * Computes a sha3-256 hash of the serialized tx
     */
    hash(): Buffer;
    /**
     * Computes a sha3-256 hash which can be used to verify the signature
     */
    getMessageToVerifySignature(): Buffer;
    /**
     * Returns the public key of the sender
     */
    getSenderPublicKey(): Buffer;
    /**
     * Process the v, r, s values from the `sign` method of the base transaction.
     */
    protected _processSignature(v: number, r: Buffer, s: Buffer): Transaction;
    /**
     * Returns an object with the JSON representation of the transaction
     */
    toJSON(): JsonTx;
    /**
     * Validates tx's `v` value
     */
    private _validateTxV;
    private _signedTxImplementsEIP155;
}
