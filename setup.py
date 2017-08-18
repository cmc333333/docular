from setuptools import find_packages, setup

setup(
    authors='CM Lubinski',
    author_email='cm.lubinski@gmail.com',
    install_requires=[
        'django~=1.11.0',
        'django-treebeard',
        'networkx',
        'jsonfield',
    ],
    name='docular',
    packages=find_packages(),
    version='0.0.0',
)
