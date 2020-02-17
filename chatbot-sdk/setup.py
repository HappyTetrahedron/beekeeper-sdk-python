import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
with open("../beekeeper-sdk/beekeeper_sdk/VERSION", "r") as fh:
    version = fh.read()
setuptools.setup(
    name='beekeeper_chatbot_sdk',
    version=version,
    scripts=[],
    author="Aline Abler",
    author_email="aline.abler@beekeeper.io",
    description="SDK for creating chat bots with the Beekeeper API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beekpr/beekeeper-sdk-python",
    install_requires=['beekeeper_sdk=={}'.format(version), 'pubnub', 'cryptography'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
