# "commonkeys.py" from libTWLPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libTWLPy

import binascii

prod_key = 'af1bf516a807d21aea45984f04742861'
dev_key = 'a1604a6a7123b529ae8bec32c816fcaa'
debug_key = 'a2fdddf2e423574ae7ed8657b5ab19d3'


def get_common_key(common_key_index) -> bytes:
    """
    Gets the specified DSi Common Key based on the index provided.

    Possible values for common_key_index: 0: Production Key, 1: Development Key, 2: Debugger Key

    Parameters
    ----------
    common_key_index : int
        The index of the common key to be returned.

    Returns
    -------
    bytes
        The specified common key, in binary format.
    """
    match common_key_index:
        case 0:
            common_key_bin = binascii.unhexlify(prod_key)
        case 1:
            common_key_bin = binascii.unhexlify(dev_key)
        case 2:
            common_key_bin = binascii.unhexlify(debug_key)
        case _:
            raise ValueError("The common key index provided, " + str(common_key_index) + ", does not exist.")
    return common_key_bin
