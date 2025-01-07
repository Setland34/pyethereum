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
        seed (str): The seed to generate the private key and address from.

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
            handle_message(d)
        # Is block
        elif len(d) == 3:
            handle_block(obj)
    except Exception as e:
        logging.error("Error processing object: %s", str(e))

def handle_message(d):
    """
    Handle a received message.

    Args:
        d (list): The decoded message.

    Returns:
        str: The response to the message, or None if no response is needed.
    """
    try:
        if d[0] == 'getobj':
            return get_object(d[1][0])
        elif d[0] == 'getbalance':
            return get_balance(d[1][0])
        elif d[0] == 'getcontractroot':
            return get_contract_root(d[1][0])
        elif d[0] == 'getcontractsize':
            return get_contract_size(d[1][0])
        elif d[0] == 'getcontractstate':
            return get_contract_state(d[1][0], d[1][1])
    except Exception as e:
        logging.error("Error handling message: %s", str(e))
    return None

def handle_block(obj):
    """
    Handle a received block.

    Args:
        obj (str): The serialized block data.

    Returns:
        None
    """
    try:
        blk = Block(obj)
        p = blk.prevhash
        parent = get_block(p)
        if not parent:
            logging.warning("Parent block not found")
            return
        uncles = blk.uncles
        for s in uncles:
            if not get_block(s):
                logging.warning("Uncle block not found")
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
        logging.error("Error handling block: %s", str(e))

def get_object(obj_hash):
    """
    Get an object from the database.

    Args:
        obj_hash (str): The hash of the object to get.

    Returns:
        str: The object data, or None if the object is not found.
    """
    try:
        return db.Get(obj_hash)
    except:
        try:
            return mainblk.state.db.get(obj_hash)
        except:
            return None

def get_balance(address):
    """
    Get the balance of an address.

    Args:
        address (str): The address to get the balance for.

    Returns:
        int: The balance of the address, or None if the address is not found.
    """
    try:
        return mainblk.get_balance(address)
    except:
        return None

def get_contract_root(address):
    """
    Get the root of the contract associated with an address.

    Args:
        address (str): The address to get the contract root for.

    Returns:
        str: The contract root, or None if the address is not found.
    """
    try:
        return mainblk.get_contract(address).root
    except:
        return None

def get_contract_size(address):
    """
    Get the size of the contract associated with an address.

    Args:
        address (str): The address to get the contract size for.

    Returns:
        int: The contract size, or None if the address is not found.
    """
    try:
        return mainblk.get_contract(address).get_size()
    except:
        return None

def get_contract_state(address, key):
    """
    Get the state of the contract associated with an address.

    Args:
        address (str): The address to get the contract state for.
        key (str): The key to get the state for.

    Returns:
        str: The contract state, or None if the address is not found.
    """
    try:
        return mainblk.get_contract(address).get(key)
    except:
        return None

def get_block(block_hash):
    """
    Get a block from the database.

    Args:
        block_hash (str): The hash of the block to get.

    Returns:
        Block: The block, or None if the block is not found.
    """
    try:
        return Block(db.Get(block_hash))
    except:
        return None
