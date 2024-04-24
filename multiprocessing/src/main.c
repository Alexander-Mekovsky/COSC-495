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
    MultiHandle multi_handle;
    FILE *stream;
} ThreadArguments;

void enforce_call_rate(ThreadControl *control);
size_t write_data(void *ptr, size_t size, size_t nmemb, ThreadArguments *data);
void make_call(ThreadArguments *args);

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
    MultiHandle handle = curlMultiInit();

    ThreadArguments *thread_args = malloc(sizeof(ThreadArguments));
    if (!thread_args)
    {
        pyerr(PyExc_RuntimeError, "failed to allocate ThreadArguments.");
        return NULL;
    }
    thread_args->control = &control;
    thread_args->queue = queue;
    thread_args->multi_handle = handle;
    setMultiOptions(thread_args->multi_handle,&(Option){CURLMOPT_PIPELINING, CURLPIPE_MULTIPLEX},1);

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
    if(createThreads(rate_limiter, NULL, enforce_call_rate, (void *)control, 1)[0] != 0){
        pyerr(PyExc_RuntimeError, "failed to create rate_limiter thread");
        return NULL;
    }

    int num_threads = MAX_CALLS_PER_SECOND * floor(AVG_CALL_DELAY);
    pthread_t caller[num_threads];
    int ccresults[num_threads] = createThreads(caller, NULL, make_call, (void *)thread_args, num_threads);
    for(int i = 0; i < num_threads; ++i){
        if(ccresults[i] != 0){
            pyerr(PyExc_RuntimeError, "failed to create a caller thread");
            return NULL;
        }
    }

    processMultiHandle(thread_args->multi_handle);

    joinThreads(caller,num_threads);
    setTerminate(&control);
    joinThreads(rate_limiter, 1);

    close(&thread_args->stream);
    curlMultiCleanup(thread_args->multi_handle);
    free(thread_args);
    destroyControl(&control);
    queueClear(&queue);
    queueDestroy(&queue);
    curlCleanup();

    return Py_BuildValue("s", "done");
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

void enforce_call_rate(void *control)
{
    ThreadControl *control = (ThreadControl *)args;

    while (1)
    {
        sleep(1);
        if(isTerminate(control))
            return 0;

        resetRate(control, MAX_CALLS_PER_SECOND);
        decrementQueued(control, MAX_CALLS_PER_SECOND);
    }
}

size_t write_data(void *ptr, size_t size, size_t nmemb, void *data)
{
    ThreadArguments *fileControl = (ThreadArguments *)data;
    PrivateHandleData *handleData;
    curl_easy_getinfo(curl_handle, CURLINFO_PRIVATE, &handleData);


    if(!handleData || handleData->error_flag == 1)
        return NULL;

    if(handleData->parse_start != NULL){
        gettimeofday(&handleData->req_end, NULL);
        gettimeofday(&handleData->parse_start, NULL);
    }
    xmlNode *root = xmlDocGetRootElement(xmlCtxtGetDoc(handleData->context));
    if(safeFetchContent(root,"//status/statusCode") != "" || safeFetchContent(root,  "//status/statusText") != ""){
        queueEnqueue(fileControl->queue, handleData->url);
        handleData->error_flag = 1;
        return -1;
    }
    
    int lastChunk = parseChunkedXMLResponse(handleData->context,(const char *)ptr,(size_t) size, fileControl->stream);

    if(lastChunk) {
        gettimeofday(&handleData->parse_end, NULL);
    }
    return size * nmemb;
}

void make_call(void *args)
{
    ThreadArguments *args = (ThreadArguments *)arg;
    TaskQueue *queue = args->queue;
    ThreadControl *control = args->control;

    char *endpoint;
    while ((endpoint = (char *)queueDequeue(queue)) != NULL){
        CURL *handle = curlEasyInit();
        if(handle){
            PrivateHandleData *handleData =  (HandleData *)malloc(sizeof(HandleData));
            if(handleData){
                handleData->context = xmlCreatePushParserCtxt(NULL, NULL, NULL, 0, NULL);
                handleData->url = endpoint;
                handleData->error_flag = 0;
                Option options[] = {
                    {CURLOPT_URL, endpoint},
                    {CURLOPT_WRITEDATA, (void*) args},
                    {CURLOPT_WRITEFUNCTION, write_data},
                    {CURLOPT_PRIVATE, handleData}
                };
                setEasyOptions(handle, options, 4);

                if (DEBUG && DEBUG_LVL > 2){
                    curl_easy_setopt(handle, CURLOPT_VERBOSE, 1L);
                }

                limitRate(control, MAX_CALLS_PER_SECOND);
                CURLMcode res = addMultiHandle(args->multi_handle, handle);
                gettimeofday(&handleData->req_start, NULL);

                if(res != 0){
                    pyerr(PyExc_RuntimeError, easyError(res));
                    queueEnqueue(queue, endpoint);
                    continue;
                }
            }
        }
    }
}