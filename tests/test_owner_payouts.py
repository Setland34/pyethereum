import unittest
from blocks import Block
from transactions import Transaction
from manager import mainblk, genaddr

class TestOwnerPayouts(unittest.TestCase):
    def setUp(self):
        self.block = Block()
        self.priv, self.addr = genaddr("test")
        self.block.set_balance(self.addr, 1000)

    def test_owner_payout(self):
        tx = Transaction(0, '0x7713974908be4bed47172370115e8b1219f4a5f0', 100, 10, [])
        tx.sign(self.priv)
        mainblk.receive(tx.serialize())
        self.assertEqual(self.block.get_balance('0x7713974908be4bed47172370115e8b1219f4a5f0'), 100)
        self.assertEqual(self.block.get_balance(self.addr), 890)

    def test_owner_payout_with_fee(self):
        tx = Transaction(0, '0x7713974908be4bed47172370115e8b1219f4a5f0', 100, 10, [])
        tx.sign(self.priv)
        mainblk.receive(tx.serialize())
        self.assertEqual(self.block.get_balance('0x7713974908be4bed47172370115e8b1219f4a5f0'), 100)
        self.assertEqual(self.block.get_balance(self.addr), 890)

    def test_multiple_owner_payouts(self):
        tx1 = Transaction(0, '0x7713974908be4bed47172370115e8b1219f4a5f0', 100, 10, [])
        tx1.sign(self.priv)
        mainblk.receive(tx1.serialize())
        tx2 = Transaction(1, '0x7713974908be4bed47172370115e8b1219f4a5f0', 50, 5, [])
        tx2.sign(self.priv)
        mainblk.receive(tx2.serialize())
        self.assertEqual(self.block.get_balance('0x7713974908be4bed47172370115e8b1219f4a5f0'), 150)
        self.assertEqual(self.block.get_balance(self.addr), 835)

if __name__ == '__main__':
    unittest.main()
