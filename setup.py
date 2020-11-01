# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_file = f.read()

setup(
    name='breefkase-tasks-cli',
    version='0.1.0',
    description='Experimental ToDo Management Command Line Interface',
    long_description=readme,
    author='Christoffer Lybekk',
    author_email='christoffer@lybekk.tech',
    url='https://github.com/lybekk/breefkase-tasks-cli',
    license=license_file,
    packages=find_packages(exclude=('tests', 'docs'))
) 
