import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="petutils",
    version="0.0.1",
    author="Miguel Simon",
    author_email="miguel@listenic.com",
    description="Utilities for PETALO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miguelsimon/petutils",
    packages=['petutils'],
    install_requires=[
        'numpy',
        'pandas',
        'h5py',
        'scipy',
        'matplotlib',
    ]
)
