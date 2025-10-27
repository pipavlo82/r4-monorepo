from setuptools import setup, find_packages

setup(
    name="r4sdk",
    version="0.1.5",
    description="Re4ctoR Randomness SDK Client",
    author="Pavlo Tvardovskyi",
    author_email="you@example.com",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
)
