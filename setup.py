from setuptools import setup, find_packages

setup(
    name="biblioteka",
    version="0.1.0",
    description="System zarządzania biblioteką",
    author="Kamil Amarasekara",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "biblioteka=biblioteka.cli:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "coverage>=7.0",
            "mypy>=1.0",
            "black>=24.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
