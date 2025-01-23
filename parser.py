import rlp

def parse(inp):
    """
    Parses the input data and returns a dictionary with the parsed data.

    Args:
        inp (bytes): The input data to be parsed.

    Returns:
        dict: A dictionary containing the parsed data.
    """
    if inp[0] == '\x00':
        return { "type": "transaction", "data": rlp.parse(inp[1:]) }
    else:
        return { "type": "unknown", "data": inp }
