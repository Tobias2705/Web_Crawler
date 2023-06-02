from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="WebCrawler",
    version="1.0",
    description="A web crawler used for osint purpose",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    url="https://github.com/Tobias2705/Web_Crawler",
    install_requires=[
        "PyQt5 >= 5.15.9",
        "click >= 8.1.3",
        "lxml >= 4.9.2",
        "nltk >= 3.8.1",
        "numpy >= 1.24.2",
        "pandas >= 1.5.3",
        "scikit-learn >= 1.2.1",
        "selenium >= 4.8.3",
        "beautifulsoup4 >= 4.11.2",
        "requests >= 2.28.2",
        "matplotlib >= 3.7.1",
        "torch >= 2.0.1",
        "transformers >= 4.29.2"
    ],
    python_requires=">=3.11.2",
    entry_points={
        'console_scripts': [
                'wcrawler = WebCrawler.cli.cli:cli'
        ]
    }
)
