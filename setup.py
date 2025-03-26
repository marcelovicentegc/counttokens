from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vtex_ai_tools",
    version="0.1.0",
    author="Marcelo Vicente",
    author_email="marcelovicentegc@gmail.com",
    description="A CLI tool for counting tokens in text datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vtex/ai-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vtexai=cli.cli:main",
        ],
    },
)