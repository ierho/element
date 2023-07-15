from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.2.9'
DESCRIPTION = 'Element.io SDK'
LONG_DESCRIPTION = 'app.element.io SDK based on matrix_client. The usage is very similar to discord.py'

# Setting up
setup(
    name="element-sdk",
    version=VERSION,
    author="ierhon",
    author_email="<ierhonl@proton.me>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['element', 'matrix', 'matrix_client', 'SDK', 'discord.py', 'bots'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)