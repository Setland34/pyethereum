import rlp
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def parse(inp):
    """
    Parse the input data and return the corresponding object.

    Args:
        inp (str): The input data to parse.

    Returns:
        dict: A dictionary containing the parsed object with its type and data.

    Raises:
        ValueError: If the input data is invalid or cannot be parsed.
    """
    try:
        if inp[0] == '\x00':
            return {"type": "transaction", "data": rlp.decode(inp[1:])}
        elif inp[0] == '\x01':
            return {"type": "block", "data": rlp.decode(inp[1:])}
        elif inp[0] == '\x02':
            return {"type": "message", "data": rlp.decode(inp[1:])}
        else:
            raise ValueError("Invalid input data")
    except Exception as e:
        logging.error("Error parsing input data: %s", str(e))
        raise ValueError("Failed to parse input data") from e
