#!/usr/bin/env python3
from setuptools import setup

setup(
    name='commit-message-validator',
    version='0.1.0',
    author='Bryan Davis',
    author_email='bd808@wikimedia.org',
    url='https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines',
    license='GPL-2.0+',
    description='Validate the format of a commit message to Wikimedia Gerrit standards',
    # long_description=open('README.rst').read(),
    packages=['commit_message_validator'],
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': [
            'commit-message-validator = commit_message_validator:main'
        ],
    }
)
