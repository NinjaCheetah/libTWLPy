# "content.py" from libTWLPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libTWLPy
#
# See https://wiibrew.org/wiki/Title for details about how titles are formatted

import hashlib
from .types import ContentRecord
from .crypto import decrypt_content, encrypt_content


class Content:
    """
    A Content object to parse the content stored in a TAD. Allows for retrieving content from the region in both
    encrypted or decrypted form, and setting new content.

    Attributes
    ----------
    content_record : ContentRecord
        The content record for the content stored in the region.
    """

    def __init__(self):
        self.content_record = None
        self.content_record: ContentRecord
        self.content: bytes = b''

    def load(self, content: bytes, content_record: ContentRecord) -> None:
        """
        Loads the raw content.

        Parameters
        ----------
        content : bytes
            The raw data for the content being loaded.
        content_record : ContentRecord
            The content record for the loaded content.
        """
        self.content_record = content_record
        self.content = content

    def get_enc_content(self) -> bytes:
        """
        Gets the encrypted content of the TAD.

        Returns
        -------
        bytes
            The encrypted content.
        """
        return self.content

    def get_content(self, title_key: bytes) -> bytes:
        """
        Gets the decrypted content of the TAD.

        Parameters
        ----------
        title_key : bytes
            The Title Key for the title the content is from.

        Returns
        -------
        bytes
            The decrypted content.
        """
        # Decrypt the specified content with the provided Title Key.
        content_dec = decrypt_content(self.content, title_key, self.content_record.content_size)
        # Hash the decrypted content and ensure that the hash matches the one in the Content Record.
        # If it does not, then something has gone wrong in the decryption, and an error will be thrown.
        content_dec_hash = hashlib.sha1(content_dec).hexdigest()
        content_record_hash = str(self.content_record.content_hash.decode())
        # Compare the hash and throw a ValueError if the hash doesn't match.
        if content_dec_hash != content_record_hash:
            raise ValueError("Content hash did not match the expected hash in its record! The incorrect Title Key may "
                             "have been used!.\n"
                             "Expected hash is: {}\n".format(content_record_hash) +
                             "Actual hash is: {}".format(content_dec_hash))
        return content_dec

    def set_enc_content(self, enc_content: bytes, cid: int, content_type: int, content_size: int,
                        content_hash: bytes) -> None:
        """
        Sets new encrypted content. Hashes and size of the content are set in the content record.

        Parameters
        ----------
        enc_content : bytes
            The new encrypted content to set.
        cid : int
            The Content ID to assign the new content in the content record.
        content_type : int
            The type of the new content.
        content_size : int
            The size of the new encrypted content when decrypted.
        content_hash : bytes
            The hash of the new encrypted content when decrypted.
        """
        # Reassign all the content record values.
        self.content_record.content_id = cid
        self.content_record.content_type = content_type
        self.content_record.content_size = content_size
        self.content_record.content_hash = content_hash
        # Load the new content.
        self.content = enc_content

    def set_content(self, dec_content: bytes, cid: int, content_type: int, title_key: bytes) -> None:
        """
        Sets the provided index to a new content with the provided Content ID. Hashes and size of the content are
        set in the content record, with a new record being added if necessary.

        Parameters
        ----------
        dec_content : bytes
            The new decrypted content to set.
        cid : int
            The Content ID to assign the new content in the content record.
        content_type : int
            The type of the new content.
        title_key : bytes
            The Title Key that matches the new decrypted content.
        """
        # Store the size of the new content.
        dec_content_size = len(dec_content)
        # Calculate the hash of the new content.
        dec_content_hash = str.encode(hashlib.sha1(dec_content).hexdigest())
        # Encrypt the content using the provided Title Key and index.
        enc_content = encrypt_content(dec_content, title_key)
        # Pass values to set_enc_content()
        self.set_enc_content(enc_content, cid, content_type, dec_content_size, dec_content_hash)
