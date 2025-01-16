import unittest
from blocks import Block
from transactions import Transaction
from manager import genaddr, mainblk

class TestOwnerPayouts(unittest.TestCase):

    def setUp(self):
        self.block = Block()
        self.owner_address = '0x7713974908be4bed47172370115e8b1219f4a5f0'
        self.sender_priv, self.sender_address = genaddr("sender")
        self.receiver_priv, self.receiver_address = genaddr("receiver")
        self.block.set_balance(self.sender_address, 1000)

    def test_handle_owner_payout(self):
        self.block.handle_owner_payout(self.sender_address, 100)
        owner_balance = self.block.get_balance(self.owner_address)
        self.assertEqual(owner_balance, 100)

    def test_pay_fee_with_owner_payout(self):
        self.block.pay_fee(self.sender_address, 50)
        owner_balance = self.block.get_balance(self.owner_address)
        self.assertEqual(owner_balance, 50)

    def test_transaction_with_owner_payout(self):
        tx = Transaction(0, self.receiver_address, 100, 10, [])
        tx.sign(self.sender_priv)
        mainblk.receive(tx.serialize())
        owner_balance = self.block.get_balance(self.owner_address)
        self.assertEqual(owner_balance, 100)

if __name__ == '__main__':
    unittest.main()
