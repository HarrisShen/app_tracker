from setuptools import find_packages, setup

setup(
    name='trackerflask',
    version='0.4.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)