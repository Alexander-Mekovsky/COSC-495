from setuptools import setup, Extension

module = Extension('caller',
                   sources=[
                       'src/main.c',
                       'src/network.c',
                       'src/xml_utils.c',
                       'src/threading.c',
                       'src/task_queue.c',
                       'src/py_utils.c'
                   ],
                   libraries=['curl', 'pthread', 'xml2'],
                   include_dirs=['include']  # Pointing to the directory where the header files are stored
                  )

setup(
    name='MyApiCallPackage',
    version='1.0',
    description='Package to make concurrent API calls and write to files',
    ext_modules=[module]
)