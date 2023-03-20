from setuptools import find_packages, setup

setup(
    name='trackerflask',
    version='0.5.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)