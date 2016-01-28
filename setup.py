"""
wxbreads
----------------

Small handy snippets of wxpython
"""
from setuptools import setup
import wxbreads

setup(
    name='wxbreads',
    version=wxbreads.__version__,
    url='https://github.com/lixxu/wxbreads',
    license='BSD',
    author=wxbreads.__author__,
    author_email='xuzenglin@gmail.com',
    description='Small handy snippets of wxpython',
    long_description=__doc__,
    packages=['wxbreads'],
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
