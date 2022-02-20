from setuptools import setup, find_packages

requires = [
    'astunparse',
]


setup(
    name='Parseo',
    version='0.0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requires,
)

