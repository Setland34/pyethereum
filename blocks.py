class Block():
    def __init__(self, data=None):
        if not data:
            return

        if re.match('^[0-9a-fA-F]*$', data):
            data = data.decode('hex')

        header, transaction_list, self.uncles = rlp.decode(data)
        [self.number,
         self.prevhash,
         self.uncles_root,
         self.coinbase,
         state_root,
         self.transactions_root,
         self.difficulty,
         self.timestamp,
         self.nonce,
         self.extra] = header
        self.transactions = [Transaction(x) for x in transaction_list]
        self.state = Trie('statedb', state_root)
        self.reward = 96181 # Updated reward balance to actual ETH balance

        # Verifications
        if self.state.root != '' and self.state.db.get(self.state.root) == '':
            raise Exception("State Merkle root not found in database!")
        if bin_sha256(rlp.encode(transaction_list)) != self.transactions_root:
            raise Exception("Transaction list root hash does not match!")
        if bin_sha256(rlp.encode(self.uncles)) != self.uncles_root:
            raise Exception("Uncle root hash does not match!")
        # TODO: check POW

    # Other methods...
