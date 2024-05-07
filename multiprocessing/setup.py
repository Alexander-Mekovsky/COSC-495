from setuptools import setup, Extension
import os

module = Extension('myapicall',
                   sources=[
                       'src/main.c',
                       'src/curl_utils.c',
                       'src/xml_utils.c',
                       'src/threading.c',
                       'src/task_queue.c',
                       'src/py_utils.c'
                   ],
                   libraries=['curl', 'pthread', 'xml2'],
                   include_dirs=[os.path.join('include'), '/usr/include/libxml2'], 
                   extra_compile_args=['-Wall', '-g']
                  )

setup(
    name='MyApiCallPackage',
    version='1.0',
    description='Package to make concurrent API calls and write to files',
    ext_modules=[module],
    author='Joshua Brull',
    author_email='jbrull1@gulls.salisbury.edu'
)