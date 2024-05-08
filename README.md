# libTWLPy
libTWLPy is a modern Python 3 library for interacting with and editing files from the DSi. It aims to be simple to use, well maintained, and offer as many features as reasonably possible in one library, so that a newly-written Python program could reasonably do 100% of its DSi-related work with just one library. It also aims to be fully cross-platform, so that any tools written with it can also be cross-platform.

libTWLPy is directly based off of my other library [libWiiPy](https://github.com/NinjaCheetah/libWiiPy), which is designed for handing files from the Wii. While it has already diverged quite a bit from being a direct copy of libWiiPy, general feature and efficiency improvements that apply to both libraries are likely to be ported.

# Features
This list will expand as libTWLPy is developed, but these features are currently available:
- TMD, ticket, and TAD parsing
- TAD content extraction, decryption, re-encryption, and packing (A first-of-its-kind feature!)
- Downloading titles from the NUS

# Usage
The easiest way to get libWiiPy for your project is to install the latest version of the library from PyPI, as shown below. 
```sh
pip install -U libTWLPy
```
Our PyPI project page can be found [here](https://pypi.org/project/libTWLPy/).

Because libTWLPy is very early in development, you may want to use the latest version of the package via git instead, so that you have the latest features available. You can do that like this:
```sh
pip install -U git+https://github.com/NinjaCheetah/libTWLPy
```
Please be aware that because libTWLPy is in a very early state right now, many features may be subject to change, and methods and properties available now have the potential to disappear in the future.

# Building
To build this package locally, the steps are quite simple, and should apply to all platforms. Make sure you've set up your `venv` first!

First, install the dependencies from `requirements.txt`:
```sh
pip install -r requirements.txt
```

Then, build the package using the Python `build` module:
```sh
python -m build
```

And that's all! You'll find your compiled pip package in `dist/`.

# Special Thanks
This project wouldn't be possible without all the research and documentation that previous members of the DSi modding scene have done, and especially would not be possible without the extensive work done by [@rvtr](https://github.com/rvtr) that really made everything come together. Thanks, Lillian!

## Special Thanks to WiiBrew and DSiBrew Contributors
Thank you to all the contributors to the documentation on the WiiBrew and DSiBrew pages that make this all understandable! Some of the key articles referenced are as follows:
- [Title metadata](https://wiibrew.org/wiki/Title_metadata), for the documentation on how a TMD is structured
- [WAD files](https://wiibrew.org/wiki/WAD_files), for the documentation on how a WAD is structured (which then carries over into TADs)
- [Title database](https://dsibrew.org/wiki/Title_database), for documentation on what titles are available on the NUS
