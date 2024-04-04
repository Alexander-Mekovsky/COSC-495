To compile the C extension use the function: 
python setup.py build_ext --inplace
or use python3
This will build a shared library for the python script to use the modules in the C extension

Then just run the python file:
python multapicall.py
or use python3