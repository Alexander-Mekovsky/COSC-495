#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <fcntl.h>
#include "../include/network.h"
#include "../include/py_utils.h"
#include "../include/task_queue.h"
#include "../include/threading.h"
#include "../include/xml_utils.h"

#define MAX_CALLS_PER_SECOND 9
#define AVG_CALL_DELAY 4 // 3.50818417867
#define DEBUG 1
#define DEBUG_LVL 1

typedef struct ThreadArguments
{
    TaskQueue *queue;
    ThreadControl *control;
    MultiHandle multi_handle;
    XPathFields *fields;
    FILE *stream;
} ThreadArguments;

typedef struct WriteData
{
    ThreadArguments *targs;
    CURL *easy_handle;
    int firstChunk;
} WriteData;

void *enforce_call_rate(void *args);
size_t write_data(char *ptr, size_t size, size_t nmemb, void *userdata);
void *make_call(void *args);

static PyObject *get_response(PyObject *self, PyObject *args){
    int error = 0;
    PyObject *error_typ;
    char *error_msg;

    PyObject *listObj;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &listObj)) {
        pyerr(PyExc_TypeError, "Invalid arguments. Expected a list.");
        return Py_BuildValue("s", "error");
    }

    size_t len = PyList_Size(listObj);
    if (len == 0){
        pyerr(PyExc_RuntimeError, "Invalid arguments. Expected at least one URL.");
        return Py_BuildValue("s", "error");
    }

    char **arr = malloc(len * sizeof(char*));
    if (arr == NULL) {
        pyerr(PyExc_MemoryError, "Memory allocation failed for URL array.");
        return Py_BuildValue("s", "error");
    }

    if(pylistToStrings(listObj, arr, len) != 0){
        free(arr);
        pyerr(PyExc_RuntimeError, "Unable to create string array.");
        return Py_BuildValue("s", "error");
    }
    
    TaskQueue *queue = queueFromArr(arr, 1, len);
    char *filename = strdup(arr[0]);
    for (size_t i = 0; i < len; ++i) {
        free(arr[i]);
    }
    free(arr);

    fprintf(stderr, "%s\n", filename);
    FILE *stream = fopen(filename, "w+");
    if (!stream) {
        free(filename);
        queueDestroy(queue);
        pyerr(PyExc_IOError, "Failed to open file for writing.");
        return Py_BuildValue("s", "error");
    }
    fprintf(stream, "ID,Source ID,ISSN,EISSN,ISBN,Title,Creator,Publication Name,Cover Date,Cited By,Type,Subtype,Article Number,Volume,DOI,Affiliation\n");

    CURLcode res;
    if((res = curlInit()) != 0){
        const char *msg = easyError(res);
        pyerr(PyExc_RuntimeError, msg);
        return Py_BuildValue("s", "error");
    }

    ThreadControl *control = controlInit();
    MultiHandle handle = curlMultiInit();
    XPathFields *fields = (XPathFields *)malloc(sizeof(XPathFields));
    if (fields)
        memset(fields, 0, sizeof(XPathFields));
    if (setScopusFieldXPaths(fields) < 0){
        destroyControl(control);
        queueDestroy(queue);
        curlCleanup();
        pyerr(PyExc_RuntimeError, "failed to allocate XPathFields.");
        return Py_BuildValue("s", "error");
    }

    ThreadArguments *thread_args = malloc(sizeof(ThreadArguments));
    if (!thread_args)
    {   
        cleanupXPathFields(fields);
        destroyControl(control);
        queueDestroy(queue);
        curlCleanup();
        pyerr(PyExc_RuntimeError, "failed to allocate ThreadArguments.");
        return Py_BuildValue("s", "error");
    }
    thread_args->control = control;
    thread_args->queue = queue;

    thread_args->multi_handle = handle;
    curl_multi_setopt(thread_args->multi_handle.multi_handle,CURLMOPT_PIPELINING, CURLPIPE_MULTIPLEX);
    
    thread_args->fields = fields;

    thread_args->stream = stream;

    pthread_t rate_limiter;
    if(createThreads(&rate_limiter, NULL, enforce_call_rate, (void *)control, 1) == 0){
        int num_threads = MAX_CALLS_PER_SECOND * floor(AVG_CALL_DELAY);
        
        pthread_t caller[num_threads];
        if(createThreads(caller, NULL, make_call, (void *)thread_args, num_threads) == 0){
            processMultiHandle(&thread_args->multi_handle, isQueued, control);
        } else {
            joinThreads(caller,num_threads);
            error = 1;
            error_typ = PyExc_RuntimeError;
            error_msg = "failed to create one or more caller threads";
        }
    }

    setTerminate(control);
    joinThreads(&rate_limiter, 1);

    fclose(thread_args->stream);
    free(filename);
    curlMultiCleanup(&thread_args->multi_handle);
    free(thread_args);
    cleanupXPathFields(fields);
    destroyControl(control);
    queueDestroy(queue);
    curlCleanup();
    if(error){
        pyerr(error_typ, error_msg);
        return NULL;
    }
    return Py_BuildValue("s", "done");
}

static PyMethodDef MyApiCallMethods[] = {
    {"get_response", (PyCFunction)get_response, METH_VARARGS, "Function to get response from API endpoints."},
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

void *enforce_call_rate(void *args)
{
    ThreadControl *control = (ThreadControl *)args;

    while (1)
    {
        sleep(1);
        if(isTerminate(control))
            return NULL;

        resetRate(control, MAX_CALLS_PER_SECOND);
        decrementQueued(control, MAX_CALLS_PER_SECOND);
    }
}

size_t write_data(char *ptr, size_t size, size_t nmemb, void *userdata)
{
    WriteData *wd = (WriteData *)userdata;
    ThreadArguments *fileControl = wd->targs;
    XPathFields *fields = fileControl->fields;
    PrivateHandleData *handleData;
    curl_easy_getinfo(wd->easy_handle, CURLINFO_PRIVATE, &handleData);

    if (handleData == NULL || handleData->context == NULL) {
        fprintf(stderr, "Error: Null pointer encountered in critical data structures.\n");
        return -1; 
    }

    if(wd->firstChunk){
        gettimeofday(&handleData->req_end, NULL);
        gettimeofday(&handleData->parse_start, NULL);
        wd->firstChunk = 0;

        if(parseChunkedXMLResponse(handleData->context,(const char *)ptr,(size_t) size * nmemb, fileControl->stream, fields) < 0)
            return -1;
    }       

    int lastChunk = 0;
    if(!wd->firstChunk)
        if((lastChunk = parseChunkedXMLResponse(handleData->context,(const char *)ptr,(size_t) size * nmemb, fileControl->stream,fields)) < 0)
            return -1;

    if(lastChunk) {
        gettimeofday(&handleData->parse_end, NULL);
        free(wd);
    }
    return size * nmemb;
}

void *make_call(void *args)
{
    ThreadArguments *targs = (ThreadArguments *)args;
    TaskQueue *queue = targs->queue;
    ThreadControl *control = targs->control;

    char *endpoint;
    while ((endpoint = (char *)queueDequeue(queue)) != NULL){
        CURL *handle = curlEasyInit();
        if(handle){
            PrivateHandleData *handleData =  (PrivateHandleData *)malloc(sizeof(PrivateHandleData));
            if(handleData){
                handleData->context = xmlCreatePushParserCtxt(NULL, NULL, NULL, 0, NULL);
                handleData->url = endpoint;
                handleData->error_flag = 0;
                
                WriteData *wd = malloc(sizeof(WriteData));
                if (!wd) {
                    return NULL;
                }
                wd->targs = targs;
                wd->easy_handle = handle;
                wd->firstChunk = 1;

                // Option options[] = {
                //     {CURLOPT_URL, (char *) endpoint},
                //     {CURLOPT_WRITEDATA, (void *) wd},
                //     {CURLOPT_WRITEFUNCTION, (void *)write_data},
                //     {CURLOPT_PRIVATE, (void *)handleData}
                // };
                // setEasyOptions(handle, options, 4);

                curl_easy_setopt(handle, CURLOPT_URL,endpoint);
                curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void *)wd);
                curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION,write_data);
                curl_easy_setopt(handle, CURLOPT_PRIVATE, handleData);

                

                if (DEBUG && DEBUG_LVL > 2){
                    curl_easy_setopt(handle, CURLOPT_VERBOSE, 1L);
                }

                limitRate(control, MAX_CALLS_PER_SECOND);
                CURLMcode res = addMultiHandle(&targs->multi_handle, handle);
                gettimeofday(&handleData->req_start, NULL);

                if(res != 0){
                    pyerr(PyExc_RuntimeError, multiError(res));
                    queueEnqueue(queue, endpoint);
                    continue;
                }
            }
        }
    }
    return NULL;
}