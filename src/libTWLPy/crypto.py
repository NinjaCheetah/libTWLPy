# "crypto.py" from libTWLPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libTWLPy

from .commonkeys import get_common_key
from .shared import convert_tid_to_iv

from Crypto.Cipher import AES


def decrypt_title_key(title_key_enc: bytes, common_key_index: int, title_id: bytes | str) -> bytes:
    """
    Gets the decrypted version of the encrypted Title Key provided.

    Requires the index of the common key to use, and the Title ID of the title that the Title Key is for.

    Parameters
    ----------
    title_key_enc : bytes
        The encrypted Title Key.
    common_key_index : int
        The index of the common key used to encrypt the Title Key.
    title_id : bytes, str
        The Title ID of the title that the key is for.

    Returns
    -------
    bytes
        The decrypted Title Key.
    """
    # Load the correct common key for the title.
    common_key = get_common_key(common_key_index)
    # Convert the IV into the correct format based on the type provided.
    title_key_iv = convert_tid_to_iv(title_id)
    # The IV will always be in the same format by this point, so add the last 8 bytes.
    title_key_iv = title_key_iv + (b'\x00' * 8)
    # Create a new AES object with the values provided.
    aes = AES.new(common_key, AES.MODE_CBC, title_key_iv)
    # Decrypt the Title Key using the AES object.
    title_key = aes.decrypt(title_key_enc)
    return title_key


def encrypt_title_key(title_key_dec: bytes, common_key_index: int, title_id: bytes | str) -> bytes:
    """
    Encrypts the provided Title Key with the selected common key.

    Requires the index of the common key to use, and the Title ID of the title that the Title Key is for.

    Parameters
    ----------
    title_key_dec : bytes
        The decrypted Title Key.
    common_key_index : int
        The index of the common key used to encrypt the Title Key.
    title_id : bytes, str
        The Title ID of the title that the key is for.

    Returns
    -------
    bytes
        An encrypted Title Key.
    """
    # Load the correct common key for the title.
    common_key = get_common_key(common_key_index)
    # Convert the IV into the correct format based on the type provided.
    title_key_iv = convert_tid_to_iv(title_id)
    # The IV will always be in the same format by this point, so add the last 8 bytes.
    title_key_iv = title_key_iv + (b'\x00' * 8)
    # Create a new AES object with the values provided.
    aes = AES.new(common_key, AES.MODE_CBC, title_key_iv)
    # Encrypt Title Key using the AES object.
    title_key = aes.encrypt(title_key_dec)
    return title_key


def decrypt_content(content_enc, title_key, content_length) -> bytes:
    """
    Decrypts the provided content. This requires the content length to adjust padding as necessary.

    Parameters
    ----------
    content_enc : bytes
        The encrypted content.
    title_key : bytes
        The Title Key for the title the content is from.
    content_length : int
        The length in the TMD's content record of the content being decrypted.

    Returns
    -------
    bytes
        The decrypted content.
    """
    # TADs only have one content, so the IV is always all 0 bytes.
    content_iv = b'\x00' * 16
    # Align content to 16 bytes to ensure that it works with AES encryption.
    if (len(content_enc) % 16) != 0:
        content_enc = content_enc + (b'\x00' * (16 - (len(content_enc) % 16)))
    # Create a new AES object with the values provided, with the content's unique ID as the IV.
    aes = AES.new(title_key, AES.MODE_CBC, content_iv)
    # Decrypt the content using the AES object.
    content_dec = aes.decrypt(content_enc)
    # Trim additional bytes that may have been added so the content is the correct size.
    content_dec = content_dec[:content_length]
    return content_dec


def encrypt_content(content_dec, title_key) -> bytes:
    """
    Encrypts the provided content. This requires the content length to adjust padding as necessary.

    Parameters
    ----------
    content_dec : bytes
        The decrypted content.
    title_key : bytes
        The Title Key for the title the content is from.

    Returns
    -------
    bytes
        The encrypted content.
    """
    # TADs only have one content, so the IV is always all 0 bytes.
    content_iv = b'\x00' * 16
    # Calculate the intended size of the encrypted content.
    enc_size = len(content_dec) + (16 - (len(content_dec) % 16))
    # Align content to 16 bytes to ensure that it works with AES encryption.
    if (len(content_dec) % 16) != 0:
        content_dec = content_dec + (b'\x00' * (16 - (len(content_dec) % 16)))
    # Create a new AES object with the values provided, with the content's unique ID as the IV.
    aes = AES.new(title_key, AES.MODE_CBC, content_iv)
    # Encrypt the content using the AES object.
    content_enc = aes.encrypt(content_dec)
    # Trim down the encrypted content.
    content_enc = content_enc[:enc_size]
    return content_enc
