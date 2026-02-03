from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py3dbc",
    version="1.0.0",
    author="Sarth Satpute",
    author_email="sarthsatpute18@gmail.com",
    description="3D Bin Packing for Containers - Maritime optimization with ship stability physics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SarthSatpute/py3dbc",
    project_urls={
        "Bug Tracker": "https://github.com/SarthSatpute/py3dbc/issues",
        "Documentation": "https://github.com/SarthSatpute/py3dbc#readme",
        "Source Code": "https://github.com/SarthSatpute/py3dbc",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "py3dbp>=1.1.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    keywords="3d-bin-packing, container-optimization, maritime, ship-stability, logistics, cargo",
    license="MIT",
)