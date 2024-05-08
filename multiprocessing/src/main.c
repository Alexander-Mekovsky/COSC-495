#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <fcntl.h>
#include "../include/xml_utils.h"
#include "../include/curl_utils.h"
#include "../include/py_utils.h"
#include "../include/task_queue.h"
#include "../include/threading.h"


#define MAX_CALLS_PER_SECOND 8
#define AVG_CALL_DELAY 4 // 3.50818417867
#define DEBUG 1
#define DEBUG_LVL 1

typedef struct ThreadArguments
{
    TaskQueue *queue; //test
    ThreadControl *control;
    MultiHandle *multi_handle;
    XPathFields *fields;
    FILE *stream;
    FILE *log;
    int log_out;
    int responseCount;
    pthread_mutex_t count_lock;
} ThreadArguments;

typedef struct WriteData
{
    CURL *easy_handle;
    int firstChunk;
} WriteData;

void *enforce_call_rate(void *args);
size_t write_data(char *ptr, size_t size, size_t nmemb, void *userdata);
void *make_call(void *args);
void *parse_call(void *args);

// add null checking for functions and arrays
static PyObject *get_response(PyObject *self, PyObject *args){
    PyObject *listObj;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &listObj)) {
        pyerr(PyExc_TypeError,"Invalid arguments. Expected a list.");
        return Py_BuildValue("s", "Error occurred.");
    }

    size_t len = PyList_Size(listObj);
    if (len <= 0){
        pyerr(PyExc_RuntimeError,"Invalid arguments. Expected at least one.");
        return Py_BuildValue("s", "Error occurred.");
    }

    char **arr = malloc(len * sizeof(char*));
    if (arr == NULL) {
        pyerr(PyExc_MemoryError,"Memory allocation failed for URL array.");
        return Py_BuildValue("s", "Error occurred.");
    }

    PyObject *error_type = NULL;  // This will hold the Python exception type
    const char *error_msg = NULL;  // This will hold the error message string

    if(pylistToStrings(listObj, arr, len) != 0){
        error_type = PyExc_RuntimeError;
        error_msg = "Failed to create an array of strings from list";
        goto fail_arr;
    }

    TaskQueue *queue = queueFromArr(arr, 1, len);
    if(!queue){
        error_type = PyExc_MemoryError;
        error_msg = "Failed to create a queue from an array of strings";
        goto fail_queue;
    }

    CURLcode res;
    if((res = curlInit()) != 0){
        error_type = PyExc_RuntimeError;
        error_msg = easyError(res);
        goto fail_curl;
    }

    ThreadControl *control = controlInit();
    if(!control){
        error_type = PyExc_IOError;
        error_msg = "Memory allocation failed for ThreadControl.";
        goto fail_control;
    }

    MultiHandle *handle = multiInit();
    if(!handle){
        error_type = PyExc_IOError;
        error_msg = "Memory allocation failed for MultiHandle.";
        goto fail_multi;
    }

    XPathFields *fields = (XPathFields *)malloc(sizeof(XPathFields));
    if (!fields) {
        error_type = PyExc_IOError;
        error_msg = "Memory allocation failed for XPathFields.";
        goto fail_fields;
    }
    memset(fields, 0, sizeof(XPathFields));
    if (setScopusFieldXPaths(fields) < 0){
        error_type = PyExc_RuntimeError;
        error_msg = "Failed to set XPath fields properly.";
        goto fail_fields;
    }

    ThreadArguments *thread_args = malloc(sizeof(ThreadArguments));
    if (!thread_args){
        error_type = PyExc_IOError;
        error_msg = "Memory allocation failed for ThreadArguments.";
        goto fail_args;
    }
    thread_args->control = control;
    thread_args->queue = queue;

    thread_args->multi_handle = handle;
    curl_multi_setopt(handle->multi_handle,CURLMOPT_PIPELINING, CURLPIPE_MULTIPLEX);
    
    thread_args->fields = fields;
    thread_args->responseCount = 0;
    pthread_mutex_init(&thread_args->count_lock, NULL);

    char *filename = strdup(arr[0]);
    FILE *stream = fopen(filename, "w+");
    if (!stream) {
        error_type = PyExc_IOError;
        error_msg = "Failed to open file(stream) for writing";
        goto fail_stream;
    }

    FILE *log = NULL;
    thread_args->log_out = 0;
    if(DEBUG){
        time_t now = time(NULL);
        struct tm *tm_now = localtime(&now);

        char logname[256];  // Make sure the buffer is large enough
        snprintf(logname, sizeof(logname), "log/[%d-%02d-%02d:[%02d:%02d]]log.csv",
                 tm_now->tm_year + 1900,  
                 tm_now->tm_mon + 1,      
                 tm_now->tm_mday,         
                 tm_now->tm_hour,         
                 tm_now->tm_min);
        log = fopen(logname, "w+");
        if(!log){
            error_type = PyExc_IOError;
            error_msg = "Failed to open file(log) for writing"; 
            goto fail_log;
        }
        fprintf(log, "FILENAME, REQUEST TIME(sec), REQUEST TIME(sec)\n");
        thread_args->log = log;
        thread_args->log_out = 1;
    }
                
    fprintf(stream, "ID,Source ID,ISSN,EISSN,ISBN,Title,Creator,Publication Name,Cover Date,Cited By,Type,Subtype,Article Number,Volume,DOI,Affiliation\n");
    thread_args->stream = stream;

    if(!error_msg){
        pthread_t rate_limiter;
        if(createThreads(&rate_limiter, NULL, enforce_call_rate, (void *)thread_args, 1) == 0){
            int num_threads = MAX_CALLS_PER_SECOND * floor(AVG_CALL_DELAY);
        
            pthread_t caller[num_threads];
            if(createThreads(caller, NULL, make_call, (void *)thread_args, num_threads) == 0){
                
                pthread_t parser;
                if(createThreads(&parser, NULL, parse_call,(void *)thread_args,1) != 0){
                    error_type = PyExc_RuntimeError;
                    error_msg = "Failed to create parser_thread.";
                    performMulti(handle, isQueued, (void *) control);
                    while(isQueued(thread_args->control)){
                        completeMultiTransfers(handle, NULL, 0, NULL, NULL, NULL);
                    }
                } else {
                    performMulti(handle,isQueued, (void *) control);
                    joinThreads(&parser, 1);
                }

                completeMultiTransfers(thread_args->multi_handle,thread_args->log,thread_args->log_out,thread_args->stream,parseXMLFile, thread_args->fields);
                
                joinThreads(caller, num_threads);
    
            } else {
                error_type = PyExc_RuntimeError;
                error_msg = "Failed to create one or more caller threads";
            }
            
            setTerminate(control);
            joinThreads(&rate_limiter, 1);
        }
    }

fail_log:
    if(log){
        fclose(log);
        log = NULL;
    } 

fail_stream:
    fclose(stream);
    stream = NULL;
    free(filename);
    filename = NULL;

fail_args:
    pthread_mutex_destroy(&thread_args->count_lock);
    free(thread_args);

fail_fields:
    cleanupXPathFields(fields);

fail_multi:
    cleanupMulti(handle);

fail_control:
    cleanupControl(control);

fail_curl:
    cleanupCurl();

fail_queue:
    if(!queueIsEmpty(queue)){
        FILE *outq = fopen("endpointsNotRead.txt", "w+");
        if(outq){
            while(!queueIsEmpty(queue)){
                fprintf(outq, "%s\n", (char *) queueDequeue(queue));
            }
            fclose(outq);
        }
    }
    queueDestroy(queue);

fail_arr:
    // for(size_t i = 0; i < len; ++i){
    //     if(arr[i]) free(arr[i]);
    // }
    free(arr);
    arr = NULL;
    
    if(error_msg){
        pyerr(error_type, error_msg);
        return Py_BuildValue("s", "Error occurred.");;
    }
 
    return Py_BuildValue("s", "Done.");
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
    ThreadArguments *targs = (ThreadArguments *)args;
    ThreadControl *control = targs->control;
    MultiHandle *handle = targs->multi_handle;

    while (1)
    {
        sleep(1);
        if(isTerminate(control))
            return NULL;
        usleep(40000);
        wakeupMulti(handle);
        resetRate(control, MAX_CALLS_PER_SECOND);
        wakeupMulti(handle);
        decrementQueued(control, MAX_CALLS_PER_SECOND);
    }
}

size_t write_data(char *ptr, size_t size, size_t nmemb, void *userdata)
{
    CURL *handle = (CURL *)userdata;
    if (handle == NULL) {
        fprintf(stderr, "Error: Null pointer encountered in callback(CURL *).\n");
        return 0; 
    }
    PrivateHandleData *privateData = NULL;

    curl_easy_getinfo(handle, CURLINFO_PRIVATE, &privateData);
    if(privateData == NULL){
        fprintf(stderr, "Error: Null pointer encountered in callback(PrivateHandleData *).\n");
        fprintf(stderr, "%s\n", ptr);
        return size *nmemb;
    }

    if(privateData->firstChunk){
        privateData->firstChunk = 0;
        gettimeofday(&privateData->req_end, NULL);
    }

    if (privateData->stream == NULL) {
        fprintf(stderr, "Error: Null pointer encountered in callback (FILE *).\n");
        return 0;
    }

    fprintf(privateData->stream, "%s", ptr);
    
    return size * nmemb;
}

void *make_call(void *args)
{
    ThreadArguments *targs = (ThreadArguments *)args;
    TaskQueue *queue = targs->queue;
    ThreadControl *control = targs->control;

    char *endpoint;
    while ((endpoint = (char *)queueDequeue(queue)) != NULL){
        CURL *handle = easyInit();
        if(handle){
            PrivateHandleData *handleData =  (PrivateHandleData *)malloc(sizeof(PrivateHandleData));
            if(handleData){
                memset(handleData, 0, sizeof(PrivateHandleData));
                FILE *fp;

                pthread_mutex_lock(&targs->count_lock);
                int responseNumber = targs->responseCount++;
                pthread_mutex_unlock(&targs->count_lock);

                char *filename = malloc(256); // Ensure this is large enough for your data
                if (filename != NULL) {
                    snprintf(filename, 256, "/tmp/response_%d.xml", responseNumber);
                    fp = fopen(filename, "wb");
                } 
                

                if (fp == NULL)
                {
                    fprintf(stderr, "Error: Cannot read file: %s\n",filename);
                    return (void*)101; // Return an error code if file opening fails
                }
                handleData->filename = filename;
                handleData->stream = fp;
                handleData->firstChunk = 1;
                handleData->url = endpoint;

                curl_easy_setopt(handle, CURLOPT_URL,endpoint);
                curl_easy_setopt(handle, CURLOPT_PRIVATE, handleData);

                curl_easy_setopt(handle, CURLOPT_WRITEDATA, (void *)handle);
                curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION,write_data);

                if (DEBUG && DEBUG_LVL > 2){
                    curl_easy_setopt(handle, CURLOPT_VERBOSE, 1L);
                }

                limitRate(control, MAX_CALLS_PER_SECOND);

                
                CURLMcode res = addMultiEasy(targs->multi_handle, handle);
                struct timeval tv;
                gettimeofday(&tv, NULL);
                time_t now = tv.tv_sec;
                struct tm *tm_now = localtime(&now);
                int milliseconds = tv.tv_usec / 1000;
                fprintf(stderr,"%02d:%02d:%02d-%03d: Added Handle\n", tm_now->tm_hour, tm_now->tm_min, tm_now->tm_sec, milliseconds);
                
                gettimeofday(&handleData->req_start, NULL);

                if(res != CURLM_OK){
                    fprintf(stderr, "%s\n",multiError(res));
                    queueEnqueue(queue, endpoint);
                    cleanupEasy(handle);
                    continue;
                }
            }
        }
    }
    return NULL;
}

void *parse_call(void *args){
    ThreadArguments *targs = (ThreadArguments *) args;
    int counts[5];
    for(int i = 0; i < 5; i++) counts[i] = 0;
    while(isQueued(targs->control)){
        TransfersStatus stat = completeMultiTransfers(targs->multi_handle,targs->log,targs->log_out,targs->stream,parseXMLFile, targs->fields);
        switch (stat.res)
        {
        case 0:
            break;
        case 1:
            fprintf(stderr, "Error: Bad Multi Handle\n");
            counts[1]++;
            break;
        case 2:
            fprintf(stderr, "Error: Bad Private Data\n");
            counts[2]++;
            break;
        case 3: 
            fprintf(stderr, "Error: Failed to cleanup easy handle\n");
            counts[3]++;
            break;
        default:
            fprintf(stderr, "Status error code: %d. Queueing failed endpoint\n", stat.res);
            queueEnqueue(targs->queue, stat.url);
            counts[4]++;
            break;
        }
    }
    return (void *) 0;
}