#include <Python.h>
#include <curl/curl.h>
#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>

#define MAX_CALLS_PER_SECOND 7
#define AVG_CALL_DELAY 4 // 3.50818417867
#define DEBUG 1
#define DEBUG_LVL 1

// Structure representing a task queue
// Values:
//   char *endpoint:
//   struct Task *next:
typedef struct Task
{
    char *endpoint;
    struct Task *next;
} Task;

// Structure representing a task queue
// Values:
//   Task *head:
//   Task *tail:
//   pthread_mutex_t lock:
typedef struct TaskQueue
{
    Task *head;
    Task *tail;
    pthread_mutex_t lock;
} TaskQueue;

// Structure to control thread behavior
typedef struct ThreadControl
{
    int terminate_flag;
    pthread_mutex_t terminate_lock;
    int calls_this_second;
    pthread_mutex_t calls_mutex;
    pthread_cond_t can_call;
    CURLM *mhandle;
    pthread_mutex_t mhandle_mutex;
} ThreadControl;

// Structure representing arguments to be passed to a thread
// Values:
//   TaskQueue *queue:
//   ThreadControl *control:
//   FILE *stream:
//   pthread_mutex_t file_lock:
typedef struct ThreadArguments
{
    TaskQueue *queue;
    ThreadControl *control;
    FILE *stream;
    pthread_mutex_t file_lock;
} ThreadArguments;

typedef struct HandleData
{
    char *url;
    xmlParserCtxtPtr context;
    struct timeval start;
    struct timeval end;
} HandleData;

void *increment_calls_this_second(ThreadControl *, char *);
void *mydequeue(TaskQueue *);
void clear_task_queue(TaskQueue *);
size_t write_data(void *, size_t, size_t, WriteData *);
void *make_data(void *);
void *enforce_call_rate(void *);

// Function to get response from API endpoints
// Parameters:
//   self: The Python object
//   args: The arguments passed from Python (expects a list of API endpoints) The first item in the list should be the output file for the data requested.
// Returns:
//   "done" on success, or NULL on failure
static PyObject *get_response(PyObject *self, PyObject *args)
{
    PyObject *listObj;

    if (!PyArg_ParseTuple(args, "O", &listObj))
    {
        PyErr_SetString(PyExc_TypeError, "invalid arguments, expected a list object.");
        return NULL;
    }

    if (!PyList_Check(listObj))
    {
        PyErr_SetString(PyExc_TypeError, "parameter must be a list.");
        return NULL;
    }

    TaskQueue *tqueue = malloc(sizeof(TaskQueue));
    if (!tqueue)
    {
        PyErr_SetString(PyExc_RuntimeError, "failed to allocate TaskQueue.");
        return NULL;
    }
    tqueue->head = NULL;
    tqueue->tail = NULL;
    pthread_mutex_t qlock = PTHREAD_MUTEX_INITIALIZER;
    tqueue->lock = qlock;

    PyObject *temp = PyList_GetItem(listObj, 0);
    if (!PyUnicode_Check(temp))
    {
        PyErr_SetString(PyExc_TypeError, "list items must be strings.");
        return NULL;
    }
    const char *filename = PyUnicode_AsUTF8(temp);

    size_t queueLen = PyList_Size(listObj);
    for (size_t i = 1; i < queueLen; ++i)
    {
        PyObject *temp = PyList_GetItem(listObj, i);
        if (!PyUnicode_Check(temp))
        {
            PyErr_SetString(PyExc_TypeError, "list items must be strings.");
            return NULL;
        }
        const char *endpoint = PyUnicode_AsUTF8(temp);
        myenqueue(tqueue, strdup(endpoint));
    }

    curl_global_init(CURL_GLOBAL_ALL);
    ThreadControl tcontrol = {
        .terminate_flag = 0,
        .terminate_lock = PTHREAD_MUTEX_INITIALIZER,
        .calls_this_second = 0,
        .calls_mutex = PTHREAD_MUTEX_INITIALIZER,
        .can_call = PTHREAD_COND_INITIALIZER,
        .mhandle = curl_multi_init(),
        .mhandle_mutex = PTHREAD_MUTEX_INTIALIZER};

    ThreadArguments *targs = malloc(sizeof(ThreadArguments));
    if (!targs)
    {
        PyErr_SetString(PyExc_RuntimeError, "failed to allocate ThreadArguments.");
        return NULL;
    }
    targs->control = &tcontrol;
    targs->queue = tqueue;

    FILE *s = open(filename, O_RDWR | O_CREAT, 0644);
    fprintf(s, "ID,Source ID,ISSN,EISSN,ISBN,Title,Creator,Publication Name,Cover Date,Cited By,Type,Subtype,Article Number,Volume,DOI,Affiliation\n");
    if (!stream)
    {
        PyErr_SetString(PyExcRuntimeError, "failed to open file.");
    }
    targs->stream = s;
    pthread_mutex_t flock = PTHREAD_MUTEX_INTIALIZER;
    targs->file_lock = flock;

    pthread_t rateLimiterThread;
    pthread_create(&rateLimiterThread, NULL, enforce_call_rate, (void *)&tcontrol);

    int num_threads = MAX_CALLS_PER_SECOND * floor(AVG_CALL_DELAY);
    pthread_t threads[num_threads];
    for (int i = 0; i < num_threads; i++)
    {
        if (pthread_create(&threads[i], NULL, make_call, (void *)targs) != 0)
        {
            PyErr_SetString(PyExc_RuntimeError, "Failed to create worker thread.");
            return NULL;
        }
    }

    // multi handler here (loop)

    // Wait for all calls to be finished or crash
    for (int i = 0; i < num_threads; i++)
    {
        pthread_join(threads[i], NULL);
    }

    pthread_mutex_lock(&tcontrol.mutex);
    tcontrol.terminate_flag = 1;
    pthread_mutex_unlock(&tcontrol.mutex);
    pthread_join(rateLimiterThread, NULL);

    // Clear all allocated variables
    pthread_mutex_destroy(&targs.file_lock);
    free(&targs->stream);
    pthread_mutex_destroy(&tcontrol.terminate_lock);
    pthread_mutex_destroy(&tcontrol.calls_mutex);
    pthread_cond_destroy(&tcontrol.can_call);
    pthread_mutex_destroy(&tcontrol.mhandle_mutex);
    pthread_mutex_destroy(&tqueue->lock);

    clear_task_queue(tqueue);
    free(tqueue);
    free(targs);

    return Py_BuildValue("s", "done");
}

static PyMethodDef MyApiCallMethods[] = {
    {"get_response", get_response, METH_VARARGS, "Function to get response from API endpoints."},
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

// Function to increment calls made in the current second
// Parameters:
//   control: Pointer to the ThreadControl structure
void *increment_calls_this_second(ThreadControl *control, CURL *handle)
{

    if (!curl)
    {
        return (void *)0; // Exit the thread or handle termination
    }

    pthread_mutex_lock(&control->calls_mutex);

    while (control->calls_this_second >= MAX_CALLS_PER_SECOND)
    {
        pthread_cond_wait(&control->can_call, &control->calls_mutex);
    }
    res = curl_multi_add_handle(control->mhandle, curl);

    control->calls_this_second++;
    pthread_mutex_unlock(&control->calls_mutex);
    pthread_mutex_unlock(&control->mhandle_mutex);
    CURLcode res = curl_multi_add_handle(&control->mhandle, handle);
    pthread_mutex_unlock(&control->mhandle_mutex);

    if (DEBUG && DEGUB_LVL > 0)
        fprintf(stderr, "Calls this second: %d\n", control->calls_this_second);
    return res;
}

// Function to enqueue a task into the task queue
// Parameters:
//   q: Pointer to the TaskQueue structure
//   ep: Pointer to the endpoint for the task
void myenqueue(TaskQueue *q, void *ep)
{
    Task *task = malloc(sizeof(Task));
    task->endpoint = ep;
    task->next = NULL;

    pthread_mutex_lock(&q->lock);

    if (q->tail == NULL)
    {
        q->head = q->tail = task;
    }
    else
    {
        q->tail->next = task;
        q->tail = task;
    }

    pthread_mutex_unlock(&q->lock);
}

// Function to dequeue a task from the task queue
// Parameters:
//   q: Pointer to the TaskQueue structure
// Returns:
//   Pointer to the endpoint of the dequeued task, or NULL if the queue is empty
void *mydequeue(TaskQueue *q)
{
    pthread_mutex_lock(&q->lock);

    if (q->head == NULL)
    {
        pthread_mutex_unlock(&q->lock);
        return NULL; // Queue is empty, return NULL
    }

    Task *temp = q->head;
    char *data = strdup(temp->endpoint); // Duplicate the string to return a valid pointer
    q->head = q->head->next;

    if (q->head == NULL)
    {
        q->tail = NULL;
    }

    pthread_mutex_unlock(&q->lock);
    free(temp->endpoint);
    free(temp);
    return data;
}

// Function to clear the task queue and free allocated memory
// Parameters:
//   q: Pointer to the TaskQueue structure
void clear_task_queue(TaskQueue *q)
{
    pthread_mutex_lock(&q->lock);

    while (q->head != NULL)
    {
        Task *temp = q->head;
        q->head = q->head->next;

        free(temp->endpoint); // Free the dynamically allocated endpoint string
        free(temp);           // Free the task itself
    }

    q->tail = NULL;
    pthread_mutex_unlock(&q->lock);
}

char *safe_fetch_content(xmlNode *root, const char *xpath_expr)
{
    xmlXPathContextPtr context = xmlXPathNewContext(root->doc);
    xmlXPathObjectPtr result = xmlXPathEvalExpression((const xmlChar *)xpath_expr, context);
    char *content = NULL;

    if (result != NULL && result->nodesetval != NULL && result->nodesetval->nodeNr > 0)
    {
        content = (char *)xmlNodeGetContent(result->nodesetval->nodeTab[0]);
    }
    else
    {
        content = ""; // Return an empty string if the node is not found
    }

    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
    return content;
}
void process_affiliations(xmlNode *root, char *buffer)
{
    xmlXPathContextPtr context = xmlXPathNewContext(root->doc);
    xmlXPathRegisterNs(context, (xmlChar *)"atom", (xmlChar *)"http://www.w3.org/2005/Atom");
    xmlXPathObjectPtr result = xmlXPathEvalExpression((xmlChar *)"//atom:affiliation", context);
    char affiliations[4096] = ""; // Buffer to store all affiliations

    if (result != NULL && result->nodesetval != NULL)
    {
        for (int i = 0; i < result->nodesetval->nodeNr; i++)
        {
            xmlNode *affiliation = result->nodesetval->nodeTab[i];
            char affil_parts[1024] = "";
            xmlNode *affilname = affiliation->children; // Assuming direct children here, needs proper path if nested

            // Concatenate parts
            snprintf(affil_parts, sizeof(affil_parts), "%s-%s-%s",
                     (char *)xmlNodeGetContent(xmlXPathEvalExpression((xmlChar *)"atom:affilname", context)->nodesetval->nodeTab[i]),
                     (char *)xmlNodeGetContent(xmlXPathEvalExpression((xmlChar *)"atom:affiliation-city", context)->nodesetval->nodeTab[i]),
                     (char *)xmlNodeGetContent(xmlXPathEvalExpression((xmlChar *)"atom:affiliation-country", context)->nodesetval->nodeTab[i]));

            // Append to the main affiliations buffer
            strcat(affiliations, affil_parts);
            if (i < result->nodesetval->nodeNr - 1)
            {
                strcat(affiliations, "x"); // Delimiter between multiple affiliations
            }
        }
    }

    strcpy(buffer, affiliations); // Copy the result to the output buffer
    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
}

void extract_and_write_csv(xmlNode *root_element, FILE *csvFile)
{
    // Define XPath expressions for all required fields
    const char *id_xpath = "//dc:identifier";
    const char *source_id_xpath = "//atom:source-id";
    const char *issn_xpath = "//prism:issn";
    const char *eissn_xpath = "//prism:eIssn";
    const char *isbn_xpath = "//prism:isbn";
    const char *title_xpath = "//dc:title";
    const char *creator_xpath = "//dc:creator";
    const char *publication_name_xpath = "//prism:publicationName";
    const char *cover_date_xpath = "//prism:coverDate";
    const char *cited_by_xpath = "//atom:citedby-count";
    const char *type_xpath = "//prism:aggregationType";
    const char *subtype_xpath = "//atom:subtypeDescription";
    const char *article_number_xpath = "//prism:articleNumber";
    const char *volume_xpath = "//prism:volume";
    const char *doi_xpath = "//prism:doi";
    const char *affiliation_xpath = "//prism:affiliation";

    // Fetching content safely
    char *id = safe_fetch_content(root_element, id_xpath);
    char *source_id = safe_fetch_content(root_element, source_id_xpath);
    char *issn = safe_fetch_content(root_element, issn_xpath);
    char *eissn = safe_fetch_content(root_element, eissn_xpath);
    char *isbn = safe_fetch_content(root_element, isbn_xpath);
    char *title = safe_fetch_content(root_element, title_xpath);
    char *creator = safe_fetch_content(root_element, creator_xpath);
    char *publication_name = safe_fetch_content(root_element, publication_name_xpath);
    char *cover_date = safe_fetch_content(root_element, cover_date_xpath);
    char *cited_by = safe_fetch_content(root_element, cited_by_xpath);
    char *type = safe_fetch_content(root_element, type_xpath);
    char *subtype = safe_fetch_content(root_element, subtype_xpath);
    char *article_number = safe_fetch_content(root_element, article_number_xpath);
    char *volume = safe_fetch_content(root_element, volume_xpath);
    char *doi = safe_fetch_content(root_element, doi_xpath);

    // Writing to the CSV file
    char affiliation_buffer[4096];
    process_affiliations(root_element, affiliation_buffer);

    // Write to the CSV file
    fprintf(csvFile, "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n",
            id, source_id, issn, eissn, isbn, title, creator, publication_name, cover_date, cited_by, type, subtype,
            article_number, volume, doi, affiliation_buffer);
}
// Function to write data to a file stream
// Parameters:
//   ptr: Pointer to the data to be written
//   size: Size of each element to be written
//   nmemb: Number of elements to be written
//   stream: File stream to write data into
// Returns:
//   Number of elements successfully written
size_t write_data(void *ptr, size_t size, size_t nmemb, ThreadArguments *data)
{

    ThreadArguments *fileControl = (ThreadArguments *)data;
    HandleData *handleData;
    curl_easy_get_info(curl_handle, CURLINFO_PRIVATE, &handleData);
    int lastChunk = 0;

    size_t real_size = size * nmemb;
    // Parse the current chunk of data
    if (xmlParseChunk(handleData->context, (const char *)ptr, real_size, &lastChunk))
    {
        fprintf(stderr, "Error while parsing XML chunk\n");
        return 0; // Stop further processing if there is a parsing error
    }
    if (lastChunk)
    {
        // Assuming you want to extract and write data after every chunk is parsed
        xmlNode *root_element = xmlDocGetRootElement(handleData->context->myDoc);
        if (root_element)
        {
            pthread_mutex_lock(&fileControl->file_lock);
            extract_and_write_csv(root_element, &fileControl->stream);
            pthread_mutex_unlock(&fileControl->file_lock);
        }

        free(&handleData->context);
    }

    return realSize; // Return the number of bytes processed
}

// Function representing the action of making a call (thread function)
// Parameters:
//   arg: Pointer to the ThreadArguments structure containing task queue and thread control
// Returns:
//   NULL
void *make_call(void *arg)
{
    ThreadArguments *args = (ThreadArguments *)arg;
    TaskQueue *queue = args->queue;
    ThreadControl *control = args->control;

    char *endpoint;
    while ((endpoint = (char *)mydequeue(queue)) != NULL)
        CURL *curl = curl_easy_init(); // Initialize a CURL handle
    if (curl)
    {
        HandleData *handleData = (HandleData *)malloc(sizeof(HandleData));
        if (handleData)
        {
            handleData->context = xmlCreatePushParserCtxt(NULL, NULL, NULL, 0, NULL);
            gettimeofday(&handleData->start, NULL);
            handleData->url = endpoint;

            curl_easy_setopt(curl, CURLOPT_URL, endpoint);

            if (DEBUG && DEBUG_LVL > 2)
                curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);

            WriteData wr = {args, handleData};
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, wr);
            curl_easy_setopt(curl, CURLPOT_WRITEFUNCTION, write_data);

            if ((res = increment_calls_this_second(control, curl)) == CURLE_OK)
            {
                fprintf(stderr, "curl_multi_add_handle() failed: %s\n", curl_easy_strerror(res));
                fprintf(stderr, "url: %s\n", endpoint);
            }
            curl_easy_cleanup(curl); //
            return (void *)102;      //
        }

        curl_easy_cleanup(curl); // Cleanup the CURL handle
    }
    fclose(fp);     // Close the file stream
    free(endpoint); // Free the memory allocated for the endpoint string
}
return (void *)0;
}

// Function to enforce call rate by limiting calls per second
// Parameters:
//   args: A pointer to ThreadControl structure containing thread control parameters
void *enforce_call_rate(void *args)
{
    ThreadControl *control = (ThreadControl *)args;

    while (1)
    {
        sleep(1);
        pthread_mutex_lock(&control->mutex);
        if (control->terminate_flag == 1)
        {
            pthread_mutex_unlock(&control->mutex);
            return (void *)0;
        }
        pthread_mutex_unlock(&control->mutex);

        pthread_mutex_lock(&control->calls_mutex);
        control->calls_this_second = 0;
        pthread_cond_broadcast(&control->can_call);
        pthread_mutex_unlock(&control->calls_mutex);
    }
}
