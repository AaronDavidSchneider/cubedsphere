import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cubedsphere',
    version='v0.1',
    packages=setuptools.find_packages(),
    include_package_data=True,
    url='https://github.com/AaronDavidSchneider/cubedsphere',
    license='MIT',
    author='Aaron David Schneider',
    author_email='aaron.schneider@nbi.ku.dk',
    description='Library for post processing of MITgcm cubed sphere data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "scipy",
        "numpy",
        "matplotlib",
    ]
)