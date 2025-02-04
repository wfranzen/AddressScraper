from setuptools import setup, find_packages

setup(
    name="addressScraper",
    version="2.2.1",
    author="wfranzen",
    author_email="willfranzen@gmail.com",
    description="A Python library for standardizing addresses and extracting address components",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wfranzen/AddressScraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,
)
