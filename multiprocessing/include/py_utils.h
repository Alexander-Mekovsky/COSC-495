#ifndef PY_UTILS_H
#define PY_UTILS_H

#include <Python.h>

int pyerr(PyObject *type, char *message);
size_t objToList(PyObject *obj, PyObject *list);
int pylistToStrings(PyObject *list, char **arr, size_t size); 

#endif PY_UTILS_H