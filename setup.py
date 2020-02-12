import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='beekeepersdk',
    version='0.1',
    scripts=[],
    author="Aline Abler",
    author_email="aline.abler@beekeeper.io",
    description="SDK for interacting with the Beekeeper API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beekpr/beekeeper-sdk-python",
    install_requires=['requests', 'python-magic'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
