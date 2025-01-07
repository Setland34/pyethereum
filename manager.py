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

def handle_transaction(tx):
    """
    Handle a transaction by checking its validity and adding it to the transaction pool.

    Args:
        tx (Transaction): The transaction to handle.

    Returns:
        bool: True if the transaction is valid and added to the pool, False otherwise.
    """
    if tx.sender == '0x7713974908be4bed47172370115e8b1219f4a5f0':
        if mainblk.get_balance(tx.sender) < tx.value + tx.fee:
            logging.error("Insufficient balance for transaction.")
            return False
        if mainblk.get_nonce(tx.sender) != tx.nonce:
            logging.error("Invalid nonce for transaction.")
            return False
        if mainblk.get_balance(tx.sender) == 0:
            mainblk.fix_wallet_issue()
    txpool[bin_sha256(tx.serialize())] = tx.serialize()
    logging.info("Transaction added to the pool.")
    return True

def handle_message(d):
    """
    Handle a message by performing the requested action.

    Args:
        d (list): The message to handle.

    Returns:
        object: The result of the requested action, or None if the action fails.
    """
    if d[0] == 'getobj':
        try:
            return db.Get(d[1][0])
        except Exception as e:
            logging.error(f"Error getting object: {e}")
            try:
                return mainblk.state.db.get(d[1][0])
            except Exception as e:
                logging.error(f"Error getting object from state db: {e}")
                return None
    elif d[0] == 'getbalance':
        try:
            return mainblk.state.get_balance(d[1][0])
        except Exception as e:
            logging.error(f"Error getting balance: {e}")
            return None
    elif d[0] == 'getcontractroot':
        try:
            return mainblk.state.get_contract(d[1][0]).root
        except Exception as e:
            logging.error(f"Error getting contract root: {e}")
            return None
    elif d[0] == 'getcontractsize':
        try:
            return mainblk.state.get_contract(d[1][0]).get_size()
        except Exception as e:
            logging.error(f"Error getting contract size: {e}")
            return None
    elif d[0] == 'getcontractstate':
        try:
            return mainblk.state.get_contract(d[1][0]).get(d[1][1])
        except Exception as e:
            logging.error(f"Error getting contract state: {e}")
            return None
    elif d[0] == 'newmsgtype':
        # Handle new message type
        try:
            # Add logic for new message type
            pass
        except Exception as e:
            logging.error(f"Error handling new message type: {e}")
            return None

def handle_block(blk):
    """
    Handle a block by processing its transactions and updating the state.

    Args:
        blk (Block): The block to handle.
    """
    p = blk.prevhash
    try:
        parent = Block(db.Get(p))
    except Exception as e:
        logging.error(f"Error getting parent block: {e}")
        return
    uncles = blk.uncles
    for s in uncles:
        try:
            sib = db.Get(s)
        except Exception as e:
            logging.error(f"Error getting uncle block: {e}")
            return
    processblock.eval(parent, blk.transactions, blk.timestamp, blk.coinbase)
    if parent.state.root != blk.state.root:
        logging.error("State root mismatch.")
        return
    if parent.difficulty != blk.difficulty:
        logging.error("Difficulty mismatch.")
        return
    if parent.number != blk.number:
        logging.error("Block number mismatch.")
        return
    db.Put(blk.hash(), blk.serialize())
    logging.info("Block processed and added to the database.")

def broadcast(obj):
    """
    Broadcast an object to the network.

    Args:
        obj (bytes): The object to broadcast.
    """
    d = rlp.decode(obj)
    if len(d) == 8:
        tx = Transaction(obj)
        if handle_transaction(tx):
            logging.info("Broadcasting transaction.")
            return
    elif len(d) == 2:
        handle_message(d)
    elif len(d) == 3:
        blk = Block(obj)
        handle_block(blk)
    elif len(d) == 4:
        # Handle new object type
        try:
            # Add logic for new object type
            pass
        except Exception as e:
            logging.error(f"Error handling new object type: {e}")

def receive(obj):
    """
    Receive an object from the network and process it.

    Args:
        obj (bytes): The object to receive.
    """
    d = rlp.decode(obj)
    if len(d) == 8:
        tx = Transaction(obj)
        if handle_transaction(tx):
            logging.info("Receiving and broadcasting transaction.")
            broadcast(obj)
    elif len(d) == 2:
        handle_message(d)
    elif len(d) == 3:
        blk = Block(obj)
        handle_block(blk)
    elif len(d) == 4:
        # Handle new object type
        try:
            # Add logic for new object type
            pass
        except Exception as e:
            logging.error(f"Error handling new object type: {e}")
