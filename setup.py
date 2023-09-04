# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dash_manager",
    version="1.0.0",                     
    author="Kirill Stepanov",
    author_email="stpnv.kirill.o@gmail.com",
    description="A tool for combining Dash apps on a single server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[                      
        "dash>=2.11.1",      
        "dash-iconify>=0.1.2",
        "dash-mantine-components>=0.12.1",
        "dash-bootstrap-components>=1.4.2"  ,
        "setuptools=>66.0.0"                              
    ],                                             
    url="https://github.com/stpnvkirill/dash-manager",
    packages=setuptools.find_packages(),
    classifiers=(                                 
        "Programming Language :: Python :: 3",    
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",   
    ),
)