from trie import Trie
import random
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def genkey():
    """
    Generate a random key.

    Returns:
        str: A random key.
    """
    L = random.randrange(30)
    if random.randrange(5) == 0:
        return ''
    return ''.join([random.choice('1234579qetyiasdfghjklzxcvbnm') for x in range(L)])

t = Trie('/tmp/' + genkey())

def trie_test():
    """
    Test the Trie implementation by setting and getting random keys and values.

    Raises:
        Exception: If a value retrieved from the Trie does not match the expected value.
    """
    o = {}
    for i in range(60):
        key, value = genkey(), genkey()
        if value:
            logging.info("Setting key: '%s', value: '%s'", key, value)
        else:
            logging.info("Deleting key: '%s'", key)
        o[key] = value
        t.update(key, value)
    for k in o.keys():
        v1 = o[k]
        v2 = t.get(k)
        logging.debug("Expected value: '%s', Retrieved value: '%s'", v1, v2)
        if v1 != v2:
            raise Exception("Incorrect value retrieved from Trie!")

trie_test()
