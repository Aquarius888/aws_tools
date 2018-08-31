# Copying builds from BUILDER to AWS S3

## Installation

1. git clone http://git.ringcentral.com:8888/lab/awsbuildcopy.git
2. cd awsbuildcopy
3. pip3 install -r requirements.txt
4. rename settings.py.sample to settings.py

## Usage

buildcopyaws.py copies builds from builder.dins.ru to AWS S3.
It pulls release notes from ADS (settings.py rn_name).
It copies builds of Unix and Windows components with subcomponents,
 also OPS components.
