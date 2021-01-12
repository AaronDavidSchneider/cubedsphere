import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cubedsphere',
    version='v0.1.3',
    packages=setuptools.find_packages(),
    include_package_data=True,
    url='https://github.com/AaronDavidSchneider/cubedsphere',
    download_url='https://github.com/AaronDavidSchneider/chemcomp/archive/0.1.3.zip',
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
        "xesmf",
        "esmpy",
        "xgcm",
	"xmitgcm"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
      ],
)
