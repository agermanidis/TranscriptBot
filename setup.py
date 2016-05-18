#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='TranscriptBot',
    version='0.1.2',
    description='Real-time voice transcription Slack bot',
    author='Anastasis Germanidis',
    author_email='agermanidis@gmail.com',
    url='https://github.com/agermanidis/TranscriptBot',
    packages=['transcriptbot'],
    scripts=['bin/transcriptbot'],
    install_requires=[
        'requests==2.3.0',
        'tabulate==0.7.5',
        'sounddevice==0.3.3'
    ],
    license=open("LICENSE").read()
)
