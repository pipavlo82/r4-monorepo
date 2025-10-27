from setuptools import setup, find_packages

setup(
    name='r4sdk',
    version='0.1.0',
    description='Client SDK for Re4ctoR verifiable RNG',
    author='Pavlo Tvardovskyi',
    author_email='shtomko@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
