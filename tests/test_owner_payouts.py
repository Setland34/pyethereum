import unittest
from blocks import Block
from transactions import Transaction
from trie import Trie
import rlp

class TestOwnerPayouts(unittest.TestCase):

    def setUp(self):
        self.block = Block()
        self.block.state = Trie('statedb')
        self.block.coinbase = '0x1234567890abcdef1234567890abcdef12345678'
        self.owner_address = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.sender_address = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef'
        self.receiver_address = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcdef'

        # Initialize balances
        self.block.set_balance(self.sender_address, 1000)
        self.block.set_balance(self.owner_address, 0)

    def test_owner_payout_on_transaction(self):
        tx = Transaction(1, self.receiver_address, 100, 10, [])
        tx.sender = self.sender_address
        self.block.transactions.append(tx)
        self.block.process_transactions(self.block.transactions)

        # Check balances after transaction
        self.assertEqual(self.block.get_balance(self.sender_address), 890)
        self.assertEqual(self.block.get_balance(self.owner_address), 100)

    def test_owner_payout_on_fee(self):
        tx = Transaction(1, self.receiver_address, 100, 10, [])
        tx.sender = self.sender_address
        self.block.transactions.append(tx)
        self.block.process_transactions(self.block.transactions)

        # Check balances after transaction
        self.assertEqual(self.block.get_balance(self.sender_address), 890)
        self.assertEqual(self.block.get_balance(self.owner_address), 100)

    def test_owner_payout_on_multiple_transactions(self):
        tx1 = Transaction(1, self.receiver_address, 100, 10, [])
        tx1.sender = self.sender_address
        tx2 = Transaction(2, self.receiver_address, 200, 20, [])
        tx2.sender = self.sender_address
        self.block.transactions.append(tx1)
        self.block.transactions.append(tx2)
        self.block.process_transactions(self.block.transactions)

        # Check balances after transactions
        self.assertEqual(self.block.get_balance(self.sender_address), 670)
        self.assertEqual(self.block.get_balance(self.owner_address), 300)

if __name__ == '__main__':
    unittest.main()
