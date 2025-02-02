from pybitcointools import *
import rlp
import re

class Transaction():
    """
    Represents a transaction in the Ethereum blockchain.

    Attributes:
        nonce (int): The transaction count of the sender.
        to (str): The address of the recipient.
        value (int): The amount of Ether to be transferred.
        fee (int): The transaction fee.
        data (list): Additional data included in the transaction.
        v (int): The recovery id of the transaction signature.
        r (int): The r value of the transaction signature.
        s (int): The s value of the transaction signature.
        sender (str): The address of the sender.
    """
    def __init__(*args):
        self = args[0]
        if len(args) == 2:
            self.parse(args[1])
        else:
            self.nonce = args[1]
            self.to = args[2]
            self.value = args[3]
            self.fee = args[4]
            self.data = args[5]

    def parse(self,data):
        if re.match('^[0-9a-fA-F]*$',data):
            data = data.decode('hex')
        o = rlp.unparse(data)
        self.nonce = o[0]
        self.to = o[1]
        self.value = o[2]
        self.fee = o[3]
        self.data = rlp.decode(o[4])
        self.v = o[5]
        self.r = o[6]
        self.s = o[7]
        rawhash = sha256(rlp.encode([self.nonce,self.to,self.value,self.fee,self.data]))
        pub = encode_pubkey(ecdsa_raw_recover(rawhash,(self.v,self.r,self.s)),'bin')
        self.sender = bin_sha256(pub[1:])[-20:]
        return self

    def sign(self,key):
        """
        Signs the transaction with the given private key.

        Args:
            key (str): The private key to sign the transaction.

        Returns:
            Transaction: The signed transaction.
        """
        rawhash = sha256(rlp.encode([self.to,self.value,self.fee,self.data]))
        self.v,self.r,self.s = ecdsa_raw_sign(rawhash,key)
        self.sender = bin_sha256(privtopub(key)[1:])[-20:]
        return self

    def serialize(self):
        return rlp.encode([self.nonce, self.to, self.value, self.fee, self.data, self.v, self.r, self.s])

    def hex_serialize(self):
        return self.serialize().encode('hex')

    def hash(self):
        return bin_sha256(self.serialize())
