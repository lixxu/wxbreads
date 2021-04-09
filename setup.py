"""
wxbreads
----------------

Small handy snippets of wxpython
"""
import os.path

from setuptools import setup

folder = os.path.dirname(os.path.abspath(__file__))
version = author = ""
with open(os.path.join(folder, "wxbreads/__init__.py")) as f:
    for line in f:
        if line.startswith("__version__ = "):
            version = line.split("=")[-1].strip().replace('"', "")
        elif line.startswith("__author__ = "):
            author = line.split("=")[-1].strip().replace('"', "")
            break

setup(
    name="wxbreads",
    version=version.replace("'", ""),
    url="https://github.com/lixxu/wxbreads",
    license="BSD",
    author=author.replace("'", ""),
    author_email="xuzenglin@gmail.com",
    description="Small handy snippets of wxpython",
    long_description=__doc__,
    packages=["wxbreads"],
    zip_safe=False,
    platforms="any",
    install_requires=["six"],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
