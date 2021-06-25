# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V1.1.2
    Contact: zives@seas.upenn.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "pennprov"
VERSION = "2.2.12.dev32"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "certifi>=14.05.14",
    "python-dateutil>=2.5.3",
    "six>=1.10",
    "urllib3>=1.23",
    "pandas>=1.0",
    "cachetools>=4.1",
    "sqlparse>=0.3.1",
    "omegaconf>=1.3.0",
    "psycopg2>=2.8.6",
    "pyspark>=2.0.0"
]
    

setup(
    name=NAME,
    version=VERSION,
    description="Habitat repository and authorization API",
    author_email="zives@seas.upenn.edu",
    url="https://bitbucket.org/penndb/pennprov",
    keywords=["Swagger", "Habitat repository and authorization API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Habitat API  # noqa: E501
    """
)
