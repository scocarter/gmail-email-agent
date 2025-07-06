"""
Setup script for Gmail Email Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read README
readme_content = ""
try:
    with open("README.txt", "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    readme_content = "Gmail Email Agent - Intelligent email management system"

setup(
    name="gmail-email-agent",
    version="1.0.0",
    author="Gmail Agent Team",
    author_email="dev@example.com",
    description="AI-powered Gmail inbox management and organization",
    long_description=readme_content,
    long_description_content_type="text/plain",
    url="https://github.com/username/gmail-email-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gmail-agent=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "config/*.json"],
    },
    data_files=[
        ("config", ["config/config.yaml"]),
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.8.0",
        ],
    },
)
