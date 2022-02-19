from setuptools import setup, find_packages

requires = [
    'astunparse',
]


setup(
    name='Parseo',
    version='0.0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requires,
)

