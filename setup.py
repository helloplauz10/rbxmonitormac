import setuptools

setuptools.setup(
    name="rbxmonitormac",
    version="0.0.1",
    description="A simple object oriented script that monitors roblox asynchronously without modifying and reading the game's client. This only works in MacOS",
    author="cuteuwu",
    packages=["rbxmonitor"],
    url="https://github.com/helloplauz10/rbxmonitormac/",
    license="MIT License",
    install_requires=["psutil"],
    classifiers=['Operating System :: MacOS :: MacOS X', 'Programming Language :: Python']
)
