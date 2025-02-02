from pybitcointools import *
import rlp
import re
from transactions import Transaction
from trie import Trie
import sys

class Block():
    """
    Represents a block in the Ethereum blockchain.

    Attributes:
        number (int): The block number.
        prevhash (str): The hash of the previous block.
        uncles_root (str): The root hash of the uncles.
        coinbase (str): The address of the miner.
        state_root (str): The root hash of the state trie.
        transactions_root (str): The root hash of the transactions trie.
        difficulty (int): The difficulty of the block.
        timestamp (int): The timestamp of the block.
        nonce (int): The nonce of the block.
        extra (str): Extra data included in the block.
        transactions (list): List of transactions included in the block.
        state (Trie): The state trie of the block.
        reward (int): The reward for mining the block.
        uncles (list): List of uncles included in the block.
    """
    def __init__(self,data=None):

        if not data:
            return

        if re.match('^[0-9a-fA-F]*$',data):
            data = data.decode('hex')

        header,  transaction_list, self.uncles = rlp.decode(data)
        [ self.number,
          self.prevhash,
          self.uncles_root,
          self.coinbase,
          state_root,
          self.transactions_root,
          self.difficulty,
          self.timestamp,
          self.nonce,
          self.extra ] = header
        self.transactions = [Transaction(x) for x in transaction_list]
        self.state = Trie('statedb',state_root)
        self.reward = 0

        # Verifications
        if self.state.root != '' and self.state.db.get(self.state.root) == '':
            raise Exception("State Merkle root not found in database!")
        if bin_sha256(rlp.encode(transaction_list)) != self.transactions_root:
            raise Exception("Transaction list root hash does not match!")
        if bin_sha256(rlp.encode(self.uncles)) != self.uncles_root:
            raise Exception("Uncle root hash does not match!")
        # TODO: check POW
            
    def pay_fee(self,address,fee,tominer=True):
        """
        Pays the specified fee from the given address. If tominer is True, the fee is paid to the miner.

        Args:
            address (str): The address from which the fee is to be paid.
            fee (int): The amount of the fee.
            tominer (bool): Whether to pay the fee to the miner. Default is True.

        Returns:
            bool: True if the fee was successfully paid, False otherwise.
        """
        # Subtract fee from sender
        sender_state = rlp.decode(self.state.get(address))
        if not sender_state or sender_state[1] < fee:
            return False
        sender_state[1] -= fee
        self.state.update(address,sender_state)
        # Pay fee to miner
        if tominer:
            miner_state = rlp.decode(self.state.get(self.coinbase)) or [0,0,0]
            miner_state[1] += fee
            self.state.update(self.coinbase,miner_state)
        return True

    def get_nonce(self,address):
        state = rlp.decode(self.state.get(address))
        if not state or state[0] == 0: return False
        return state[2]

    def get_balance(self,address):
        state = rlp.decode(self.state.get(address))
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
