#include "../include/py_utils.h"

// Raise a Python error with the given message and type
int pyerr(PyObject *type, const char *message) {
    PyErr_SetString(type, message);
    return 1;
}

// Convert a Python object to a Python list
size_t objToList(PyObject *obj, PyObject *list) {
    if (!PyArg_ParseTuple(obj, "O", list))
    {
        pyerr(PyExc_TypeError, "invalid arguments, expected a list object.");
        return 0;
    }

    if (!PyList_Check(list))
    {
        pyerr(PyExc_TypeError, "parameter must be a list.");
        return 0;
    }
    return PyList_Size(list);
}

// Convert a Python list to an array of C strings
int pylistToStrings(PyObject *list, char **arr, size_t size) {
    if (!PyList_Check(list)) {
        pyerr(PyExc_TypeError, "Input is not a list.");
        return 1;
    }
    
    size_t len = PyList_Size(list);
    if (len > size) {
        pyerr(PyExc_ValueError, "The size of the input list exceeds the size of the output array.");
        return 1;
    }

    for (size_t i = 0; i < len; ++i) {
        PyObject *temp = PyList_GetItem(list, i);
        if (!PyUnicode_Check(temp)) {
            pyerr(PyExc_TypeError, "All list items must be strings.");
            return 1;
        }
        
        const char *str = PyUnicode_AsUTF8(temp);
        if (!str) {
            pyerr(PyExc_RuntimeError, "Unicode conversion failed.");
            return 1;
        }
        
        arr[i] = strdup(str);  // Allocate memory and copy string
        if (!arr[i]) {  // Check for strdup failure
            pyerr(PyExc_MemoryError, "Memory allocation failed for string duplication.");
            return 1;
        }
    }
    return 0;
}
