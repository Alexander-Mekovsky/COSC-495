#ifndef PY_UTILS_H
#define PY_UTILS_H

#include <Python.h>

int pyerr(PyObject *type, char *message);
int objToList(PyObject *obj, PyObject *list);
int pylistToStrings(PyObject *list, char **arr); 

#endif PY_UTILS_H