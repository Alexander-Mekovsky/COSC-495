To compile the C extension use the function: 
python3 setup.py build_ext --inplace
python3 setup.py install

For Debugging:
valgrind --tool=memcheck --leak-check=yes python3 main.py

or use python3
This will build a shared library for the python script to use the modules in the C extension

Then just run the python file:
python main.py
or use python3