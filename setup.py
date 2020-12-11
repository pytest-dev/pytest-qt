from pathlib import Path

from setuptools import setup, find_packages


setup(
    name="pytest-qt",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"pytest11": ["pytest-qt = pytestqt.plugin"]},
    install_requires=["pytest>=3.0.0"],
    extras_require={
        "doc": ["sphinx", "sphinx_rtd_theme"],
        "dev": ["pre-commit", "tox"],
    },
    # metadata for upload to PyPI
    author="Bruno Oliveira",
    author_email="nicoddemus@gmail.com",
    description="pytest support for PyQt and PySide applications",
    long_description=Path("README.rst").read_text(encoding="UTF-8"),
    license="MIT",
    keywords="pytest qt test unittest",
    url="http://github.com/pytest-dev/pytest-qt",
    use_scm_version={"write_to": "src/pytestqt/_version.py"},
    setup_requires=["setuptools_scm"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Desktop Environment :: Window Managers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: User Interfaces",
    ],
    tests_require=["pytest"],
)
