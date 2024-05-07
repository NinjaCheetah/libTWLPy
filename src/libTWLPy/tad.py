# "tad.py" from libTWLPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libTWLPy
#
# See https://wiibrew.org/wiki/WAD_files for details about the TAD format. The WAD and TAD file formats are nearly
# identical, so WiiBrew's WAD documentation is the best reference for TADs.

import io
import binascii
from .shared import align_value, pad_bytes


class TAD:
    """
    A TAD object that allows for either loading and editing an existing TAD or creating a new TAD from raw data.

    Attributes
    ----------
    tad_cert_size : int
        The size of the TAD's certificate.
    tad_crl_size : int
        The size of the TAD's crl.
    tad_tik_size : int
        The size of the TAD's Ticket.
    tad_tmd_size : int
        The size of the TAD's TMD.
    tad_content_size : int
        The size of TAD's total content region.
    tad_meta_size : int
        The size of the TAD's meta/footer.
    """
    def __init__(self):
        self.tad_hdr_size: int = 64
        self.tad_version: bytes = b'\x00\x00'
        # === Sizes ===
        self.tad_cert_size: int = 0
        self.tad_crl_size: int = 0
        self.tad_tik_size: int = 0
        self.tad_tmd_size: int = 0
        # This is the size of the content region, which contains all app files combined.
        self.tad_content_size: int = 0
        self.tad_meta_size: int = 0
        # === Data ===
        self.tad_cert_data: bytes = b''
        self.tad_crl_data: bytes = b''
        self.tad_tik_data: bytes = b''
        self.tad_tmd_data: bytes = b''
        self.tad_content_data: bytes = b''
        self.tad_meta_data: bytes = b''

    def load(self, tad_data) -> None:
        """
        Loads raw TAD data and sets all attributes of the TAD object. This allows for manipulating an already
        existing TAD file.

        Parameters
        ----------
        tad_data : bytes
            The data for the TAD you wish to load.
        """
        with io.BytesIO(tad_data) as tad_data:
            # Read the first 8 bytes of the file to ensure that it's a WAD. This will currently reject boot2 WADs, but
            # this tool cannot handle them correctly right now anyway.
            tad_data.seek(0x0)
            tad_magic_bin = tad_data.read(8)
            tad_magic_hex = binascii.hexlify(tad_magic_bin)
            tad_magic = str(tad_magic_hex.decode())
            if tad_magic != "0000002049730000":
                raise TypeError("This does not appear to be a valid TAD file.")
            # ====================================================================================
            # Get the sizes of each data region contained within the TAD.
            # ====================================================================================
            # Header length, which will always be 64 bytes, as it is padded out if it is shorter.
            self.tad_hdr_size = 64
            # WAD version, this is always 0.
            tad_data.seek(0x06)
            self.tad_version = tad_data.read(2)
            # TAD cert size.
            tad_data.seek(0x08)
            self.tad_cert_size = int(binascii.hexlify(tad_data.read(4)), 16)
            # TAD crl size.
            tad_data.seek(0x0c)
            self.tad_crl_size = int(binascii.hexlify(tad_data.read(4)), 16)
            # TAD ticket size.
            tad_data.seek(0x10)
            self.tad_tik_size = int(binascii.hexlify(tad_data.read(4)), 16)
            # TAD TMD size.
            tad_data.seek(0x14)
            self.tad_tmd_size = int(binascii.hexlify(tad_data.read(4)), 16)
            # TAD content size.
            tad_data.seek(0x18)
            self.tad_content_size = int(binascii.hexlify(tad_data.read(4)), 16)
            # Time/build stamp for the title contained in the TAD.
            tad_data.seek(0x1c)
            self.tad_meta_size = int(binascii.hexlify(tad_data.read(4)), 16)
            # ====================================================================================
            # Calculate file offsets from sizes. Every section of the TAD is padded out to a multiple of 0x40.
            # ====================================================================================
            tad_cert_offset = self.tad_hdr_size
            # crl isn't ever used, however an entry for its size exists in the header, so its calculated just in case.
            tad_crl_offset = align_value(tad_cert_offset + self.tad_cert_size)
            tad_tik_offset = align_value(tad_crl_offset + self.tad_crl_size)
            tad_tmd_offset = align_value(tad_tik_offset + self.tad_tik_size)
            # meta isn't guaranteed to be used, but some older SDK titles use it, and not reading it breaks things.
            tad_meta_offset = align_value(tad_tmd_offset + self.tad_tmd_size)
            tad_content_offset = align_value(tad_meta_offset + self.tad_meta_size)
            # ====================================================================================
            # Load data for each TAD section based on the previously calculated offsets.
            # ====================================================================================
            # Cert data.
            tad_data.seek(tad_cert_offset)
            self.tad_cert_data = tad_data.read(self.tad_cert_size)
            # Crl data.
            tad_data.seek(tad_crl_offset)
            self.tad_crl_data = tad_data.read(self.tad_crl_size)
            # Ticket data.
            tad_data.seek(tad_tik_offset)
            self.tad_tik_data = tad_data.read(self.tad_tik_size)
            # TMD data.
            tad_data.seek(tad_tmd_offset)
            self.tad_tmd_data = tad_data.read(self.tad_tmd_size)
            # Content data.
            tad_data.seek(tad_content_offset)
            self.tad_content_data = tad_data.read(self.tad_content_size)
            # Meta data.
            tad_data.seek(tad_meta_offset)
            self.tad_meta_data = tad_data.read(self.tad_meta_size)

    def dump(self) -> bytes:
        """
        Dumps the TAD object into the raw TAD file. This allows for creating a TAD file from the data contained in
        the TAD object.

        Returns
        -------
        bytes
            The full TAD file as bytes.
        """
        tad_data = b''
        # Lead-in data.
        tad_data += b'\x00\x00\x00\x20'
        # TAD type.
        tad_data += b'\x49\x73'
        # TAD version.
        tad_data += self.tad_version
        # TAD cert size.
        tad_data += int.to_bytes(self.tad_cert_size, 4)
        # TAD crl size.
        tad_data += int.to_bytes(self.tad_crl_size, 4)
        # TAD ticket size.
        tad_data += int.to_bytes(self.tad_tik_size, 4)
        # TAD TMD size.
        tad_data += int.to_bytes(self.tad_tmd_size, 4)
        # TAD content size.
        tad_data += int.to_bytes(self.tad_content_size, 4)
        # TAD meta size.
        tad_data += int.to_bytes(self.tad_meta_size, 4)
        tad_data = pad_bytes(tad_data)
        # Retrieve the cert data and write it out.
        tad_data += self.get_cert_data()
        tad_data = pad_bytes(tad_data)
        # Retrieve the crl data and write it out.
        tad_data += self.get_crl_data()
        tad_data = pad_bytes(tad_data)
        # Retrieve the ticket data and write it out.
        tad_data += self.get_ticket_data()
        tad_data = pad_bytes(tad_data)
        # Retrieve the TMD data and write it out.
        tad_data += self.get_tmd_data()
        tad_data = pad_bytes(tad_data)
        # Retrieve the meta/footer data and write it out.
        tad_data += self.get_meta_data()
        tad_data = pad_bytes(tad_data)
        # Retrieve the content data and write it out.
        tad_data += self.get_content_data()
        tad_data = pad_bytes(tad_data)
        # Return the raw TAD file for the data contained in the object.
        return tad_data

    def get_cert_data(self) -> bytes:
        """
        Gets the certificate data from the TAD.

        Returns
        -------
        bytes
            The certificate data.
        """
        return self.tad_cert_data

    def get_crl_data(self) -> bytes:
        """
        Gets the crl data from the TAD, if it exists.

        Returns
        -------
        bytes
            The crl data.
        """
        return self.tad_crl_data

    def get_ticket_data(self) -> bytes:
        """
        Gets the ticket data from the TAD.

        Returns
        -------
        bytes
            The ticket data.
        """
        return self.tad_tik_data

    def get_tmd_data(self) -> bytes:
        """
        Returns the TMD data from the TAD.

        Returns
        -------
        bytes
            The TMD data.
        """
        return self.tad_tmd_data

    def get_content_data(self) -> bytes:
        """
        Gets the content of the TAD.

        Returns
        -------
        bytes
            The content data.
        """
        return self.tad_content_data

    def get_meta_data(self) -> bytes:
        """
        Gets the meta region of the TAD, which is typically unused.

        Returns
        -------
        bytes
            The meta region.
        """
        return self.tad_meta_data

    def set_cert_data(self, cert_data) -> None:
        """
        Sets the certificate data of the TAD. Also calculates the new size.

        Parameters
        ----------
        cert_data : bytes
            The new certificate data.
        """
        self.tad_cert_data = cert_data
        # Calculate the size of the new cert data.
        self.tad_cert_size = len(cert_data)

    def set_crl_data(self, crl_data) -> None:
        """
        Sets the crl data of the TAD. Also calculates the new size.

        Parameters
        ----------
        crl_data : bytes
            The new crl data.
        """
        self.tad_crl_data = crl_data
        # Calculate the size of the new crl data.
        self.tad_crl_size = len(crl_data)

    def set_tmd_data(self, tmd_data) -> None:
        """
        Sets the TMD data of the TAD. Also calculates the new size.

        Parameters
        ----------
        tmd_data : bytes
            The new TMD data.
        """
        self.tad_tmd_data = tmd_data
        # Calculate the size of the new TMD data.
        self.tad_tmd_size = len(tmd_data)

    def set_ticket_data(self, tik_data) -> None:
        """
        Sets the Ticket data of the TAD. Also calculates the new size.

        Parameters
        ----------
        tik_data : bytes
            The new TMD data.
        """
        self.tad_tik_data = tik_data
        # Calculate the size of the new Ticket data.
        self.tad_tik_size = len(tik_data)

    def set_content_data(self, content_data) -> None:
        """
        Sets the content data of the TAD. Also calculates the new size.

        Parameters
        ----------
        content_data : bytes
            The new content data.
        """
        self.tad_content_data = content_data
        # Calculate the size of the new content data.
        self.tad_content_size = len(content_data)

    def set_meta_data(self, meta_data) -> None:
        """
        Sets the meta data of the TAD. Also calculates the new size.

        Parameters
        ----------
        meta_data : bytes
            The new meta data.
        """
        self.tad_meta_data = meta_data
        # Calculate the size of the new meta data.
        self.tad_meta_size = len(meta_data)
