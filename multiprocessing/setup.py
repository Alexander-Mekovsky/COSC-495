from setuptools import setup, Extension

module = Extension('main',
                   sources=[
                       'src/main.c',
                       'src/network.c',
                       'src/xml_utils.c',
                       'src/threading.c',
                       'src/task_queue.c',
                       'src/py_utils.c'
                   ],
                   libraries=['curl', 'pthread', 'xml2'],
                   include_dirs=['include'], 
                   extra_compile_args=['-Wall']
                  )

setup(
    name='MyApiCallPackage',
    version='1.0',
    description='Package to make concurrent API calls and write to files',
    ext_modules=[module],
    author='Joshua Brull',
    author_email='jbrull1@gulls.salisbury.edu'
)