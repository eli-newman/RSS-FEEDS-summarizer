#!/usr/bin/env python3
"""
Setup script for RSS Feed Summarizer
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rss-feed-summarizer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An intelligent RSS feed processor that fetches, filters, ranks, summarizes, and distributes AI technology news",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rss-feed-summarizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Communications :: Email",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "email": [
            "yagmail>=0.15.293",
        ],
    },
    entry_points={
        "console_scripts": [
            "rss-summarizer=rss_feed_summarizer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rss_feed_summarizer": [
            "config/*.yaml",
            "examples/*.yaml",
            "templates/*.html",
        ],
    },
    keywords="rss, news, ai, summarization, openai, email, automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/rss-feed-summarizer/issues",
        "Source": "https://github.com/yourusername/rss-feed-summarizer",
        "Documentation": "https://github.com/yourusername/rss-feed-summarizer#readme",
    },
)
