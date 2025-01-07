from pybitcointools import *
import rlp
import re
from transactions import Transaction
from trie import Trie
import sys
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Block():
    def __init__(self, data=None):
        """
        Initialize a Block instance.

        Args:
            data (str): The serialized block data.

        Raises:
            Exception: If the state Merkle root, transaction list root hash, or uncle root hash does not match.
        """
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
        self.reward = 0

        # Verifications
        if self.state.root != '' and self.state.db.get(self.state.root) == '':
            raise Exception("State Merkle root not found in database!")
        if bin_sha256(rlp.encode(transaction_list)) != self.transactions_root:
            raise Exception("Transaction list root hash does not match!")
        if bin_sha256(rlp.encode(self.uncles)) != self.uncles_root:
            raise Exception("Uncle root hash does not match!")
        # TODO: check POW

    def pay_fee(self, address, fee, tominer=True):
        """
        Pay a fee from the sender to the miner.

        Args:
            address (str): The address of the sender.
            fee (int): The fee amount.
            tominer (bool): Whether to pay the fee to the miner.

        Returns:
            bool: True if the fee is paid successfully, False otherwise.
        """
        # Subtract fee from sender
        sender_state = rlp.decode(self.state.get(address))
        if not sender_state or sender_state[1] < fee:
            return False
        sender_state[1] -= fee
        self.state.update(address, sender_state)
        # Pay fee to miner
        if tominer:
            miner_state = rlp.decode(self.state.get(self.coinbase)) or [0, 0, 0]
            miner_state[1] += fee
            self.state.update(self.coinbase, miner_state)
        return True

    def get_nonce(self, address):
        """
        Get the nonce of an address.

        Args:
            address (str): The address to get the nonce for.

        Returns:
            int: The nonce of the address, or False if the address is not found.
        """
        state = rlp.decode(self.state.get(address))
        if not state or state[0] == 0:
            return False
        return state[2]

    def get_balance(self, address):
        """
        Get the balance of an address.

        Args:
            address (str): The address to get the balance for.

        Returns:
            int: The balance of the address, or 0 if the address is not found.
        """
        state = rlp.decode(self.state.get(address))
        return state[1] if state else 0

    def set_balance(self, address, balance):
        """
        Set the balance of an address.

        Args:
            address (str): The address to set the balance for.
            balance (int): The new balance.
        """
        state = rlp.decode(self.state.get(address)) or [0, 0, 0]
        state[1] = balance
        self.state.update(address, rlp.encode(state))

    def get_contract(self, address):
        """
        Get the contract associated with an address.

        Args:
            address (str): The address to get the contract for.

        Returns:
            Trie: The contract associated with the address, or False if the address is not found.
        """
        state = rlp.decode(self.state.get(address))
        if not state or state[0] == 0:
            return False
        return Trie('statedb', state[2])

    def update_contract(self, address, contract):
        """
        Update the contract associated with an address.

        Args:
            address (str): The address to update the contract for.
            contract (Trie): The new contract.
        """
        state = rlp.decode(self.state.get(address)) or [1, 0, '']
        if state[0] == 0:
            return False
        state[2] = contract.root
        self.state.update(address, state)

    def serialize(self):
        """
        Serialize the block.

        Returns:
            str: The serialized block data.
        """
        txlist = [x.serialize() for x in self.transactions]
        header = [self.number,
                  self.prevhash,
                  bin_sha256(rlp.encode(self.uncles)),
                  self.coinbase,
                  self.state.root,
                  bin_sha256(rlp.encode(txlist)),
                  self.difficulty,
                  self.timestamp,
                  self.nonce,
                  self.extra]
        return rlp.encode([header, txlist, self.uncles])

    def hash(self):
        """
        Get the hash of the block.

        Returns:
            str: The hash of the block.
        """
        return bin_sha256(self.serialize())
