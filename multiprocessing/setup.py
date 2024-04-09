from setuptools import setup, Extension

module = Extension('myapicall',
                    sources = ['myapicall.c'],
                    libraries = ['curl', 'pthread'])

setup(name = 'MyApiCallPackage',
      version = '1.0',
      description = 'Package to make concurrent API calls and write to files',
      ext_modules = [module])
