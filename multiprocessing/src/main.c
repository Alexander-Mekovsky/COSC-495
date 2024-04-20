#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "../include/network.h"
#include "../include/py_utils.h"
#include "../include/task_queue.h"
#include "../include/threading.h"
#include "../include/xml_utils.h"

#define MAX_CALLS_PER_SECOND 7
#define AVG_CALL_DELAY 4 // 3.50818417867
#define DEBUG 1
#define DEBUG_LVL 1

typedef struct ThreadArguments
{
    TaskQueue *queue;
    ThreadControl *control;
    FILE *stream;
    pthread_mutex_t file_lock;
} ThreadArguments;

static PyObject *get_response(PyObject *self, PyObject *thread_args){
    PyObject *listObj;
    size_t len = objToList(thread_args, &listObj);
    if(len == 0){
        pyerr(PyExc_RuntimeError, "invalid arguments. expected atleast one url");
        return NULL;
    }
    char *arr[len];
    if(pylistToStrings(listObj, &arr, len) != 0){
        pyerr(PyExc_RuntimeError, "unable to create string array.");
        return NULL;
    }
    TaskQueue *queue = queueFromArr(arr, 1, len);

    CURLcode res;
    if(res = curlInit() != 0){
        char *msg = easyError(res);
        pyerr(PyExc_RuntimeError, msg);
        return NULL;
    }

    ThreadControl *control = controlInit();

    ThreadArguments *thread_thread_args = malloc(sizeof(ThreadArguments));
    if (!thread_args)
    {
        pyerr(PyExc_RuntimeError, "failed to allocate ThreadArguments.");
        return NULL;
    }
    thread_args->control = &control;
    thread_args->queue = queue;

    FILE *stream = open(filename, O_RDWR | O_CREAT, 0644);
    fprintf(s, "ID,Source ID,ISSN,EISSN,ISBN,Title,Creator,Publication Name,Cover Date,Cited By,Type,Subtype,Article Number,Volume,DOI,Affiliation\n");
    if (!stream)
    {
        pyerr(PyExcRuntimeError, "failed to open file.");
        return NULL;
    }
    thread_args->stream = s;
    pthread_mutex_t file_lock = PTHREAD_MUTEX_INTIALIZER;
    thread_args->file_lock = file_lock;

    pthread_t rate_limiter;
    if(createThreads(rate_limiter, NULL, enforce_call_rate, (void *)control, 1) != 0){
        pyerr(PyExc_RuntimeError, "failed to create rate_limiter thread");
        return NULL;
    }

    





}

static PyMethodDef MyApiCallMethods[] = {
    {"get_response", get_response, METH_VARthread_args, "Function to get response from API endpoints."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef myapicallmodule = {
    PyModuleDef_HEAD_INIT,
    "myapicall", /* name of module */
    NULL,        /* module documentation, may be NULL */
    -1,          /* size of per-interpreter state of the module,
                   or -1 if the module keeps state in global variables. */
    MyApiCallMethods};

PyMODINIT_FUNC PyInit_myapicall(void)
{
    return PyModule_Create(&myapicallmodule);
}