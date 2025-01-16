import unittest
from blocks import Block
from transactions import Transaction
from manager import receive
from processblock import eval

class TestOwnerPayouts(unittest.TestCase):
    def setUp(self):
        self.block = Block()
        self.sender = '0x1234567890abcdef1234567890abcdef12345678'
        self.receiver = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd'
        self.owner = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.block.set_balance(self.sender, 1000)
        self.block.set_balance(self.owner, 0)

    def test_owner_payout_on_transaction(self):
        tx = Transaction(0, self.receiver, 100, 10, [])
        tx.sender = self.sender
        self.block.transactions.append(tx)
        eval(self.block, self.block.transactions, 0, self.block.coinbase)
        self.assertEqual(self.block.get_balance(self.receiver), 100)
        self.assertEqual(self.block.get_balance(self.owner), 100)

    def test_owner_payout_on_receive(self):
        tx = Transaction(0, self.receiver, 100, 10, [])
        tx.sender = self.sender
        receive(tx.serialize())
        self.assertEqual(self.block.get_balance(self.receiver), 100)
        self.assertEqual(self.block.get_balance(self.owner), 100)

    def test_owner_payout_on_multiple_transactions(self):
        tx1 = Transaction(0, self.receiver, 100, 10, [])
        tx1.sender = self.sender
        tx2 = Transaction(1, self.receiver, 200, 20, [])
        tx2.sender = self.sender
        self.block.transactions.extend([tx1, tx2])
        eval(self.block, self.block.transactions, 0, self.block.coinbase)
        self.assertEqual(self.block.get_balance(self.receiver), 300)
        self.assertEqual(self.block.get_balance(self.owner), 300)

if __name__ == '__main__':
    unittest.main()
