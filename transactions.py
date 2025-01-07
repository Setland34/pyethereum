from pybitcointools import *
import rlp
import re
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Transaction():
    def __init__(self, *args):
        """
        Initialize a Transaction instance.

        Args:
            *args: Variable length argument list. If two arguments are provided, the first is self and the second is the serialized transaction data. Otherwise, the arguments are nonce, to, value, fee, and data.

        Raises:
            Exception: If the number of arguments is not 2 or 6.
        """
        if len(args) == 2:
            self.parse(args[1])
        elif len(args) == 6:
            self.nonce = args[1]
            self.to = args[2]
            self.value = args[3]
            self.fee = args[4]
            self.data = args[5]
        else:
            raise Exception("Invalid number of arguments")

    def parse(self, data):
        """
        Parse a serialized transaction.

        Args:
            data (str): The serialized transaction data.

        Raises:
            Exception: If the data format is invalid.
        """
        if re.match('^[0-9a-fA-F]*$', data):
            data = data.decode('hex')
        o = rlp.decode(data)
        self.nonce = o[0]
        self.to = o[1]
        self.value = o[2]
        self.fee = o[3]
        self.data = rlp.decode(o[4])
        self.v = o[5]
        self.r = o[6]
        self.s = o[7]
        rawhash = sha256(rlp.encode([self.nonce, self.to, self.value, self.fee, self.data]))
        pub = encode_pubkey(ecdsa_raw_recover(rawhash, (self.v, self.r, self.s)), 'bin')
        self.sender = bin_sha256(pub[1:])[-20:]
        return self

    def sign(self, key):
        """
        Sign the transaction with a private key.

        Args:
            key (str): The private key to sign the transaction with.

        Returns:
            Transaction: The signed transaction.
        """
        rawhash = sha256(rlp.encode([self.to, self.value, self.fee, self.data]))
        self.v, self.r, self.s = ecdsa_raw_sign(rawhash, key)
        self.sender = bin_sha256(privtopub(key)[1:])[-20:]
        return self

    def serialize(self):
        """
        Serialize the transaction.

        Returns:
            str: The serialized transaction data.
        """
        return rlp.encode([self.nonce, self.to, self.value, self.fee, self.data, self.v, self.r, self.s])

    def hex_serialize(self):
        """
        Serialize the transaction and return it as a hexadecimal string.

        Returns:
            str: The serialized transaction data as a hexadecimal string.
        """
        return self.serialize().encode('hex')

    def hash(self):
        """
        Get the hash of the transaction.

        Returns:
            str: The hash of the transaction.
        """
        return bin_sha256(self.serialize())
