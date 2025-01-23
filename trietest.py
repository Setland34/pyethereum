from trie import Trie
import random

def genkey():
    L = random.randrange(30)
    if random.randrange(5) == 0: return ''
    return ''.join([random.choice('1234579qetyiasdfghjklzxcvbnm') for x in range(L)])

t = Trie('/tmp/'+genkey())

def trie_test():
    """
    Tests the Trie class by performing a series of random key-value updates and verifying the results.

    The function generates random keys and values, updates the trie with these key-value pairs, and then verifies that the values stored in the trie match the expected values.

    Raises:
        Exception: If the value retrieved from the trie does not match the expected value.
    """
    o = {}
    for i in range(60):
        key, value = genkey(), genkey()
        if value: print "setting key: '"+key+"', value: '"+value+"'"
        else: print "deleting key: '"+key+"'"
        o[key] = value
        t.update(key,value)
    for k in o.keys():
        v1 = o[k]
        v2 = t.get(k)
        print v1,v2
        if v1 != v2: raise Exception("incorrect!")
    
trie_test()    
