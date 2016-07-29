from setuptools import setup, find_packages

setup(
    name="DataCleaner",
    version="1.0",
    packages=find_packages(),
    scripts=[],  # no scripts for now
    # listing dependencies
    author="Amin",
    description="This is the DataCleaner package", requires=['os', 'json', 'pandas', 'requests', 'h5py', 'math', 'random', 're', 'numpy', 'logging', 'time'])
