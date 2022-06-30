from setuptools import setup, find_packages
from os import path
from io import open

VERSION = '0.1.6'
DESCRIPTION = 'A transition-based feature generator package for process logs.'

current_directory = path.abspath(path.dirname(__file__))

with open(path.join(current_directory, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

with open(path.join(current_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="tfgen",
    version=VERSION,
    author="Yinzheng Zhong",
    author_email="y.zhong10@liverpool.ac.uk",
    url='https://github.com/yinzheng-zhong/TFGen',
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    install_requires=requirements,
    keywords=['anomaly detection', 'machine learning', 'intrusion detection', 'process mining'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Education',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
    ]
)