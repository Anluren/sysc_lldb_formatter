#!/usr/bin/env python3
"""
Setup script for SystemC LLDB Formatters
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "SystemC LLDB Formatters - Pretty-printers for SystemC data types"

setup(
    name="sysc-lldb-formatter",
    version="1.0.0",
    author="SystemC LLDB Formatter Team",
    author_email="",
    description="LLDB pretty-printers for SystemC sc_uint and sc_int data types",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/sysc_lldb_formatter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # No external dependencies - uses LLDB's built-in Python API
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            # No command-line scripts - this is an LLDB module
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="lldb systemc debugger pretty-printer formatter",
    project_urls={
        "Bug Reports": "https://github.com/your-username/sysc_lldb_formatter/issues",
        "Source": "https://github.com/your-username/sysc_lldb_formatter",
        "Documentation": "https://github.com/your-username/sysc_lldb_formatter/blob/main/README.md",
    },
)
