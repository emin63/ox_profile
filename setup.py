"""A setuptools based setup module for ox_profile

Copyright (c) 2017, Emin Martinian

See LICENSE at the top-level of this distribution for more information.
"""

# *IMPORTANT*:  While pyproject.toml is supposedly the new standard,
# *IMPORTANT*:  it is much more complicated to get working with
# *IMPORTANT*:  anything slightly non-standard (e.g. flat-layout).
# *IMPORTANT*:  Therefore we package just using setup.py.

from os import path

from setuptools import setup, find_packages


def get_readme():
    'Get the long description from the README file'

    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'README.md')) as my_fd:
        result = my_fd.read()

    return result

setup(
    name='ox_profile',
    version='0.2.14',
    description='Tools for statistical profiling.',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url='http://github.com/emin63/ox_profile',
    author='Emin Martinian',
    author_email='emin.martinian@gmail.com',
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],


    keywords='statistical profiling',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={
        'ox_profile': ['**/*.html'],
    },
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)
