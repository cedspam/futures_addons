import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example_pkg",
    version="0.0.1",
    author="cedric lacrambe <",
    author_email="cedric.lacrambe@gmail.com",
    description="delayed execution decorators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cedspam/futures_addons",
    packages=setuptools.find_packages(),
    install_requires =['lazy_object_proxy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)