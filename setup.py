from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="counttokens",
    version="0.1.0",
    author="Marcelo Vicente",
    author_email="marcelovicentegc@gmail.com",
    description="A CLI tool for counting tokens in text datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcelovicentegc/counttokens",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "counttokens=counttokens.cli:main",
        ],
    },
)