def binary_length(n):
    """
    Calculate the binary length of a number.

    Args:
        n (int): The number to calculate the binary length for.

    Returns:
        int: The binary length of the number.
    """
    if n == 0:
        return 0
    else:
        return 1 + binary_length(n // 256)

def to_binary_array(n, L=None):
    """
    Convert a number to a binary array.

    Args:
        n (int): The number to convert.
        L (int, optional): The length of the binary array. Defaults to None.

    Returns:
        list: The binary array representation of the number.
    """
    if L is None:
        L = binary_length(n)
    if n == 0:
        return []
    else:
        x = to_binary_array(n // 256)
        x.append(n % 256)
        return x

def to_binary(n, L=None):
    """
    Convert a number to a binary string.

    Args:
        n (int): The number to convert.
        L (int, optional): The length of the binary string. Defaults to None.

    Returns:
        str: The binary string representation of the number.
    """
    return ''.join([chr(x) for x in to_binary_array(n, L)])

def from_binary(b):
    """
    Convert a binary string to a number.

    Args:
        b (str): The binary string to convert.

    Returns:
        int: The number representation of the binary string.
    """
    if len(b) == 0:
        return 0
    else:
        return from_binary(b[:-1]) * 256 + ord(b[-1])

def __decode(s, pos=0):
    """
    Decode an RLP encoded string.

    Args:
        s (str): The RLP encoded string.
        pos (int, optional): The position to start decoding from. Defaults to 0.

    Returns:
        tuple: A tuple containing the decoded object and the new position.

    Raises:
        Exception: If the byte is not supported.
    """
    if not s:
        return (None, 0)
    else:
        fchar = ord(s[pos])
    if fchar < 24:
        return (ord(s[pos]), pos + 1)
    elif fchar < 56:
        b = ord(s[pos]) - 23
        return (from_binary(s[pos + 1:pos + 1 + b]), pos + 1 + b)
    elif fchar < 64:
        b = ord(s[pos]) - 55
        b2 = from_binary(s[pos + 1:pos + 1 + b])
        return (from_binary(s[pos + 1 + b:pos + 1 + b + b2]), pos + 1 + b + b2)
    elif fchar < 120:
        b = ord(s[pos]) - 64
        return (s[pos + 1:pos + 1 + b], pos + 1 + b)
    elif fchar < 128:
        b = ord(s[pos]) - 119
        b2 = from_binary(s[pos + 1:pos + 1 + b])
        return (s[pos + 1 + b:pos + 1 + b + b2], pos + 1 + b + b2)
    elif fchar < 184:
        b = ord(s[pos]) - 128
        o, pos = [], pos + 1
        for i in range(b):
            obj, pos = __decode(s, pos)
            o.append(obj)
        return (o, pos)
    elif fchar < 192:
        b = ord(s[pos]) - 183
        b2 = from_binary(s[pos + 1:pos + 1 + b])
        o, pos = [], pos + 1 + b
        for i in range(b):
            obj, pos = __decode(s, pos)
            o.append(obj)
        return (o, pos)
    else:
        raise Exception("byte not supported: " + str(fchar))

def decode(s):
    """
    Decode an RLP encoded string.

    Args:
        s (str): The RLP encoded string.

    Returns:
        object: The decoded object.
    """
    return __decode(s)[0]

def encode(s):
    """
    Encode an object using RLP encoding.

    Args:
        s (object): The object to encode.

    Returns:
        str: The RLP encoded string.

    Raises:
        Exception: If the object type is not supported or if the integer is negative.
    """
    if isinstance(s, (int, long)):
        if s < 0:
            raise Exception("can't handle negative ints")
        elif s >= 0 and s < 24:
            return chr(s)
        elif s <= 2**256:
            b = to_binary(s)
            return chr(len(b) + 23) + b
        else:
            b = to_binary(s)
            b2 = to_binary(len(b))
            return chr(len(b2) + 55) + b2 + b
    elif isinstance(s, str):
        if len(s) < 56:
            return chr(len(s) + 64) + s
        else:
            b2 = to_binary(len(s))
            return chr(len(b2) + 119) + b2 + s
    elif isinstance(s, list):
        if len(s) < 56:
            return chr(len(s) + 128) + ''.join([encode(x) for x in s])
        else:
            b2 = to_binary(len(s))
            return chr(len(b2) + 183) + b2 + ''.join([encode(x) for x in s])
    else:
        raise Exception("Encoding for " + str(s) + " not yet implemented")
