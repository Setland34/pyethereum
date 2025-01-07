import unittest
from blocks import Block
from transactions import Transaction
from manager import receive, broadcast

class TestWalletIssue(unittest.TestCase):

    def setUp(self):
        self.block = Block()
        self.block.coinbase = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.block.reward = 1000
        self.block.set_balance(self.block.coinbase, 0)

    def test_fix_wallet_issue(self):
        self.block.fix_wallet_issue()
        self.assertEqual(self.block.get_balance(self.block.coinbase), 1000)

    def test_receive_transaction(self):
        tx = Transaction(0, '0x123', 500, 10, [])
        tx.sender = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.block.set_balance(tx.sender, 1000)
        receive(tx.serialize())
        self.assertEqual(self.block.get_balance(tx.sender), 490)
        self.assertEqual(self.block.get_balance('0x123'), 500)

    def test_broadcast_transaction(self):
        tx = Transaction(0, '0x123', 500, 10, [])
        tx.sender = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.block.set_balance(tx.sender, 1000)
        broadcast(tx.serialize())
        self.assertEqual(self.block.get_balance(tx.sender), 490)
        self.assertEqual(self.block.get_balance('0x123'), 500)

    def test_wallet_balance_zero(self):
        self.block.set_balance(self.block.coinbase, 0)
        self.block.fix_wallet_issue()
        self.assertEqual(self.block.get_balance(self.block.coinbase), 1000)

    def test_wallet_funds_return(self):
        self.block.set_balance(self.block.coinbase, 500)
        self.block.fix_wallet_issue()
        self.assertEqual(self.block.get_balance(self.block.coinbase), 500)

    def test_receive_transaction_with_zero_balance(self):
        tx = Transaction(0, '0x123', 500, 10, [])
        tx.sender = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.block.set_balance(tx.sender, 0)
        receive(tx.serialize())
        self.assertEqual(self.block.get_balance(tx.sender), 1000 - 500 - 10)
        self.assertEqual(self.block.get_balance('0x123'), 500)

    def test_broadcast_transaction_with_zero_balance(self):
        tx = Transaction(0, '0x123', 500, 10, [])
        tx.sender = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.block.set_balance(tx.sender, 0)
        broadcast(tx.serialize())
        self.assertEqual(self.block.get_balance(tx.sender), 1000 - 500 - 10)
        self.assertEqual(self.block.get_balance('0x123'), 500)

if __name__ == '__main__':
    unittest.main()
