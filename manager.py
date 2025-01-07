import rlp
import leveldb
from blocks import Block
from transactions import Transaction
import processblock
import hashlib
from pybitcointools import *
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

txpool = {}

genesis_header = [
    0,
    '',
    bin_sha256(rlp.encode([])),
    '',
    '',
    bin_sha256(rlp.encode([])),
    2**36,
    0,
    0,
    ''
]

genesis = [genesis_header, [], []]

mainblk = Block(rlp.encode(genesis))

db = leveldb.LevelDB("objects")

def genaddr(seed):
    """
    Generate a private key and address from a seed.

    Args:
        seed (str): The seed to generate the private key and address.

    Returns:
        tuple: A tuple containing the private key and address.
    """
    priv = bin_sha256(seed)
    addr = bin_sha256(privtopub(priv)[1:])[-20:]
    return priv, addr

# For testing
k1, a1 = genaddr("123")
k2, a2 = genaddr("456")

def broadcast(obj):
    """
    Broadcast an object to the network.

    Args:
        obj (str): The object to broadcast.

    Returns:
        None
    """
    pass

def receive(obj):
    """
    Receive and process an object.

    Args:
        obj (str): The object to receive and process.

    Returns:
        None
    """
    try:
        d = rlp.decode(obj)
        # Is transaction
        if len(d) == 8:
            tx = Transaction(obj)
            if mainblk.get_balance(tx.sender) < tx.value + tx.fee:
                logging.warning("Insufficient balance for transaction")
                return
            if mainblk.get_nonce(tx.sender) != tx.nonce:
                logging.warning("Invalid nonce for transaction")
                return
            txpool[bin_sha256(obj)] = obj
            broadcast(obj)
        # Is message
        elif len(d) == 2:
            if d[0] == 'getobj':
                try:
                    return db.Get(d[1][0])
                except Exception as e:
                    logging.error("Error getting object: %s", str(e))
                    try:
                        return mainblk.state.db.get(d[1][0])
                    except Exception as e:
                        logging.error("Error getting object from state db: %s", str(e))
                        return None
            elif d[0] == 'getbalance':
                try:
                    return mainblk.state.get_balance(d[1][0])
                except Exception as e:
                    logging.error("Error getting balance: %s", str(e))
                    return None
            elif d[0] == 'getcontractroot':
                try:
                    return mainblk.state.get_contract(d[1][0]).root
                except Exception as e:
                    logging.error("Error getting contract root: %s", str(e))
                    return None
            elif d[0] == 'getcontractsize':
                try:
                    return mainblk.state.get_contract(d[1][0]).get_size()
                except Exception as e:
                    logging.error("Error getting contract size: %s", str(e))
                    return None
            elif d[0] == 'getcontractstate':
                try:
                    return mainblk.state.get_contract(d[1][0]).get(d[1][1])
                except Exception as e:
                    logging.error("Error getting contract state: %s", str(e))
                    return None
        # Is block
        elif len(d) == 3:
            blk = Block(obj)
            p = blk.prevhash
            try:
                parent = Block(db.Get(p))
            except Exception as e:
                logging.error("Error getting parent block: %s", str(e))
                return
            uncles = blk.uncles
            for s in uncles:
                try:
                    sib = db.Get(s)
                except Exception as e:
                    logging.error("Error getting uncle block: %s", str(e))
                    return
            processblock.eval(parent, blk.transactions, blk.timestamp, blk.coinbase)
            if parent.state.root != blk.state.root:
                logging.warning("State root mismatch")
                return
            if parent.difficulty != blk.difficulty:
                logging.warning("Difficulty mismatch")
                return
            if parent.number != blk.number:
                logging.warning("Block number mismatch")
                return
            db.Put(blk.hash(), blk.serialize())
    except Exception as e:
        logging.error("Error processing received object: %s", str(e))
