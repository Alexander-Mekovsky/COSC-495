#include <Python.h>
#include <pthread.h>

void* thread_function(void* arg) {
    // Example function that threads will run
    printf("Thread performing task\n");
    return NULL;
}

static PyObject* start_threads(PyObject* self, PyObject* args) {
    int num_threads;
    if (!PyArg_ParseTuple(args, "i", &num_threads)) {
        return NULL;
    }

    pthread_t threads[num_threads];
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&threads[i], NULL, thread_function, NULL);
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    Py_RETURN_NONE;
}

static PyMethodDef CThreadsMethods[] = {
    {"start_threads", start_threads, METH_VARARGS, "Start multiple C threads."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cthreadsmodule = {
    PyModuleDef_HEAD_INIT,
    "cthreads",
    NULL,
    -1,
    CThreadsMethods
};

PyMODINIT_FUNC PyInit_cthreads(void) {
    return PyModule_Create(&cthreadsmodule);
}
