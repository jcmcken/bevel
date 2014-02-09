from distutils.core import setup
import bevel

setup(
  name='bevel',
  description='A simple, shell script subcommand framework',
  version=bevel.__version__,
  author=bevel.__author__,
  url='https://github.com/jcmcken/bevel',
  scripts=['bin/bevel'],
  packages=['bevel'],
  classifiers=[
    'Topic :: Utilities',
    'Operating System :: POSIX :: Linux',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: System Administrators',
    'Development Status :: 4 - Beta',
    'Topic :: System :: Shells',
    'Programming Language :: Python :: 2 :: Only',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],
)
