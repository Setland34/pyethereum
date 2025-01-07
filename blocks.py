
    
        return state[1] if state else 0

    def set_balance(self,address,balance):
        state = rlp.decode(self.state.get(address)) or [0,0,0]
        state[1] = balance
        self.state.update(address,rlp.encode(state))


    # Making updates to the object obtained from this method will do nothing. You need
    # to call update_contract to finalize the changes.
    def get_contract(self,address):
        state = rlp.decode(self.state.get(address))
        if not state or state[0] == 0: return False
        return Trie('statedb',state[2])

    def update_contract(self,address,contract):
        state = rlp.decode(self.state.get(address)) or [1,0,'']
        if state[0] == 0: return False
        state[2] = contract.root
        self.state.update(address,state)

    # Serialization method; should act as perfect inverse function of the constructor
    # assuming no verification failures
    def serialize(self):
        txlist = [x.serialize() for x in self.transactions]
        header = [ self.number,
                   self.prevhash,
                   bin_sha256(rlp.encode(self.uncles)),
                   self.coinbase,
                   self.state.root,
                   bin_sha256(rlp.encode(txlist)),
                   self.difficulty,
                   self.timestamp,
                   self.nonce,
                   self.extra ]
        return rlp.encode([header, txlist, self.uncles ])

    def hash(self):
        return bin_sha256(self.serialize())

    def fix_wallet_issue(self):
        # Logic to handle specific cases where funds return and balance shows zero
        state = rlp.decode(self.state.get(self.coinbase))
        if state and state[1] == 0:
            state[1] = self.reward
            self.state.update(self.coinbase, rlp.encode(state))
