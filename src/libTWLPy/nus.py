# "nus.py" from libTWLPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libTWLPy
#
# See https://wiibrew.org/wiki/NUS and https://dsibrew.org/wiki/NUS_Downloader/database for details about the NUS

import requests
import hashlib
from .title import Title
from .tmd import TMD
from .ticket import Ticket

nus_endpoint = "http://nus.cdn.t.shop.nintendowifi.net/ccs/download/"


def download_title(title_id: str, title_version: int = None) -> Title:
    """
    Download an entire title and all of its contents, then load the downloaded components into a Title object for
    further use. This method is NOT recommended for general use, as it has absolutely no verbosity. It is instead
    recommended to call the individual download methods instead to provide more flexibility and output.

    Parameters
    ----------
    title_id : str
        The Title ID of the title to download.
    title_version : int, option
        The version of the title to download. Defaults to latest if not set.

    Returns
    -------
    Title
        A Title object containing all the data from the downloaded title.
    """
    # First, create the new title.
    title = Title()
    # Download and load the TMD, Ticket, and certs.
    title.load_tmd(download_tmd(title_id, title_version))
    title.load_ticket(download_ticket(title_id))
    title.tad.set_cert_data(download_cert())
    # Download all contents
    title.load_content_records()
    title.content.content = download_content(title_id, title.tmd.content_record.content_id)
    # Return the completed title.
    return title


def download_tmd(title_id: str, title_version: int = None) -> bytes:
    """
    Downloads the TMD of the Title specified in the object. Will download the latest version by default, or another
    version if it was manually specified in the object.

    Parameters
    ----------
    title_id : str
        The Title ID of the title to download the TMD for.
    title_version : int, option
        The version of the TMD to download. Defaults to latest if not set.

    Returns
    -------
    bytes
        The TMD file from the NUS.
    """
    # Build the download URL. The structure is download/<TID>/tmd for latest and download/<TID>/tmd.<version> for
    # when a specific version is requested.
    tmd_url = nus_endpoint + title_id + "/tmd"
    # Add the version to the URL if one was specified.
    if title_version is not None:
        tmd_url += "." + str(title_version)
    # Make the request.
    tmd_request = requests.get(url=tmd_url,
                               headers={'User-Agent': 'Opera/9.50 (Nintendo; Opera/154; U; Nintendo DS; en)'},
                               stream=True)
    # Handle a 404 if the TID/version doesn't exist.
    if tmd_request.status_code != 200:
        raise ValueError("The requested Title ID or TMD version does not exist. Please check the Title ID and Title"
                         " version and then try again.")
    # Save the raw TMD.
    raw_tmd = tmd_request.content
    # Use a TMD object to load the data and then return only the actual TMD.
    tmd_temp = TMD()
    tmd_temp.load(raw_tmd)
    tmd = tmd_temp.dump()
    return tmd


def download_ticket(title_id: str) -> bytes:
    """
    Downloads the Ticket of the Title specified in the object. This will only work if the Title ID specified is for
    a free title.

    Parameters
    ----------
    title_id : str
        The Title ID of the title to download the Ticket for.

    Returns
    -------
    bytes
        The Ticket file from the NUS.
    """
    # Build the download URL. The structure is download/<TID>/cetk, and cetk will only exist if this is a free
    # title.
    ticket_url = nus_endpoint + title_id + "/cetk"
    # Make the request.
    ticket_request = requests.get(url=ticket_url,
                                  headers={'User-Agent': 'Opera/9.50 (Nintendo; Opera/154; U; Nintendo DS; en)'},
                                  stream=True)
    if ticket_request.status_code != 200:
        raise ValueError("The requested Title ID does not exist, or refers to a non-free title. Tickets can only"
                         " be downloaded for titles that are free on the NUS.")
    # Save the raw cetk file.
    cetk = ticket_request.content
    # Use a Ticket object to load only the Ticket data from cetk and return it.
    ticket_temp = Ticket()
    ticket_temp.load(cetk)
    ticket = ticket_temp.dump()
    return ticket


def download_cert() -> bytes:
    """
    Downloads the signing certificate used by all retail TADs. This uses the System Launcher 1.4.5U as the source.

    Returns
    -------
    bytes
        The cert file.
    """
    # Download the TMD and cetk for the System Menu 4.3U.
    tmd_url = nus_endpoint + "00030017484E4145/tmd.1792"
    cetk_url = nus_endpoint + "00030017484E4145/cetk"
    tmd = requests.get(url=tmd_url,
                       headers={'User-Agent': 'Opera/9.50 (Nintendo; Opera/154; U; Nintendo DS; en)'},
                       stream=True).content
    cetk = requests.get(url=cetk_url,
                        headers={'User-Agent': 'Opera/9.50 (Nintendo; Opera/154; U; Nintendo DS; en)'},
                        stream=True).content
    # Assemble the certificate.
    cert = b''
    # Certificate Authority data.
    cert += cetk[0x1A4 + 1024:]
    # Certificate Policy data.
    cert += tmd[0x208:0x208 + 768]
    # XS data.
    cert += cetk[0x2A4:0x2A4 + 768]
    # Since the cert is always the same, check the hash to make sure nothing went wildly wrong.
    if hashlib.sha1(cert).hexdigest() != "e583bdcdb8d4f5c06decd7ca2be46b11e6cfbac0":
        raise Exception("An unknown error has occurred downloading and creating the certificate.")
    return cert


def download_content(title_id: str, content_id: int) -> bytes:
    """
    Downloads a specified content for the title specified in the object.

    Parameters
    ----------
    title_id : str
        The Title ID of the title to download content from.
    content_id : int
        The Content ID of the content you wish to download.

    Returns
    -------
    bytes
        The downloaded content.
    """
    # Build the download URL. The structure is download/<TID>/<Content ID>.
    content_id_hex = hex(content_id)[2:]
    if len(content_id_hex) < 2:
        content_id_hex = "0" + content_id_hex
    content_url = nus_endpoint + title_id + "/000000" + content_id_hex
    # Make the request.
    content_request = requests.get(url=content_url,
                                   headers={'User-Agent': 'Opera/9.50 (Nintendo; Opera/154; U; Nintendo DS; en)'},
                                   stream=True)
    if content_request.status_code != 200:
        raise ValueError("The requested Title ID does not exist, or an invalid Content ID is present in the"
                         " content records provided.\n Failed while downloading Content ID: 000000" +
                         content_id_hex)
    content_data = content_request.content
    return content_data
