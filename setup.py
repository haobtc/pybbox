from distutils.core import setup
from setuptools import find_packages

setup(name='pybbox',
      version='0.1.0',
      description="bbox client in python",
      author='Developers',
      author_email='dev@haobtc.com',
      packages=find_packages(),
      scripts=['bin/bbox-rpc'],
      install_requires=[
          'requests'
      ]
)
