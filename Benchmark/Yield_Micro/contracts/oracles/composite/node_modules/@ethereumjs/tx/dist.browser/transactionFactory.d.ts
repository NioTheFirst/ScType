/// <reference types="node" />
import Common from '@ethereumjs/common';
import { default as Transaction } from './legacyTransaction';
import { default as AccessListEIP2930Transaction } from './eip2930Transaction';
import { TxOptions, TypedTransaction, TxData, AccessListEIP2930TxData } from './types';
export default class TransactionFactory {
    private constructor();
    /**
     * Create a transaction from a `txData` object
     *
     * @param txData - The transaction data. The `type` field will determine which transaction type is returned (if undefined, creates a legacy transaction)
     * @param txOptions - Options to pass on to the constructor of the transaction
     */
    static fromTxData(txData: TxData | AccessListEIP2930TxData, txOptions?: TxOptions): TypedTransaction;
    /**
     * This method tries to decode serialized data.
     *
     * @param data - The data Buffer
     * @param txOptions - The transaction options
     */
    static fromSerializedData(data: Buffer, txOptions?: TxOptions): TypedTransaction;
    /**
     * When decoding a BlockBody, in the transactions field, a field is either:
     * A Buffer (a TypedTransaction - encoded as TransactionType || rlp(TransactionPayload))
     * A Buffer[] (Legacy Transaction)
     * This method returns the right transaction.
     *
     * @param data - A Buffer or Buffer[]
     * @param txOptions - The transaction options
     */
    static fromBlockBodyData(data: Buffer | Buffer[], txOptions?: TxOptions): TypedTransaction;
    /**
     * This helper method allows one to retrieve the class which matches the transactionID
     * If transactionID is undefined, returns the legacy transaction class.
     *
     * @param transactionID
     * @param common
     */
    static getTransactionClass(transactionID?: number, common?: Common): typeof Transaction | typeof AccessListEIP2930Transaction;
}
