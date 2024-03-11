from distutils.core import setup, Extension

module = Extension('cthreads', sources = ['cthreads.c'])

setup(name='CThreads',
      version='1.0',
      description='Module for running C threads',
      ext_modules=[module])