from setuptools import setup, find_packages

setup(
    name="lucosms",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "requests-mock>=1.10.0",
        ],
    },
    author="Altech",
    author_email="albertabaasa07@gmail.com",
    description="Official Python SDK for Luco SMS API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/altech001/luco_sms_api",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)
