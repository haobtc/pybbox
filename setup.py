from distutils.core import setup
from setuptools import find_packages

setup(name='pybbox',
      version='0.0.5',
      description="bbox client in python",
      author='Zeng Ke',
      author_email='superisaac.ke@gmail.com',
      packages=find_packages(),
      scripts=['bin/bbox-rpc'],
      install_requires=[
          'requests'
      ]
)
