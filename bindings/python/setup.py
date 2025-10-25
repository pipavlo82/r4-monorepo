from setuptools import setup, find_packages
from pathlib import Path

README_PATH = Path(__file__).resolve().parents[2] / "README.md"
LONG_DESC = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

setup(
    name="re4ctor",
    version="0.1.0",
    author="Pavlo Tvardovskyi",
    author_email="security@re4ctor.dev",
    description="Quantum-safe entropy tap and verifiable randomness interface",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url="https://github.com/pipavlo82/r4-monorepo",
    packages=find_packages(),
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Security :: Cryptography",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.8",
)
