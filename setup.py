from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='insteon-terminal',  # Required
    version='0.1.0',  # Required
    description='A utility for interacting with insteon modems',
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/pfrommerd/insteon-terminal',
    author='Daniel Pfrommer',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='insteon',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests','config']),  # Required

    install_requires=['pyserial','logbook','setuptools'],  # Optional
    extras_require = {  # Optional
        'dev': [],
        'test': []
    },

    package_data = {  # For in-package data files
        'insteon': ['io/msg_definitions.xml'],
    },

    data_files=[('share/insteon-terminal', ['config/sys_init.py'])],  # To be installed under sys.prefix

    entry_points={  # Command line commands
        'console_scripts': [
            'insteon-terminal=insteonterminal:__main__',
        ],
    },

    project_urls={  
        'Source': 'https://github.com/pfrommerd/insteon-terminal/',
    },
)
