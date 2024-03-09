#include <Python.h>
#include <curl/curl.h>
#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define MAX_CALLS_PER_SECOND 8
#define AVG_CALL_DELAY 3.50818417867

// Structure to control thread behavior
typedef struct ThreadControl
{
    int terminate_flag;          // Flag indicating whether the thread should terminate
    int calls_this_second;       // Number of calls made in the current second
    int total_calls;             // Total number of calls made
    pthread_mutex_t mutex;       // Mutex for general thread control
    pthread_mutex_t count_mutex; // Mutex for total call count
    pthread_mutex_t calls_mutex; // Mutex for calls made in the current second
    pthread_cond_t can_call;     // Condition variable for allowing calls
} ThreadControl;

// Function to increment calls made in the current second
// Parameters:
//   control: Pointer to the ThreadControl structure
void increment_calls_this_second(ThreadControl *control)
{
    pthread_mutex_lock(&control->calls_mutex);
    while (control->calls_this_second >= MAX_CALLS_PER_SECOND)
    {
        pthread_cond_wait(&control->can_call, &control->calls_mutex);
    }
    control->calls_this_second++;
    pthread_mutex_unlock(&control->calls_mutex);
}

// Function to increment the total call count
// Parameters:
//   control: Pointer to the ThreadControl structure
void increment_call_count(ThreadControl *control)
{
    pthread_mutex_lock(&control->count_mutex);
    control->total_calls++;
    pthread_mutex_unlock(&control->count_mutex);
}

// Structure representing a task
typedef struct Task
{
    char *endpoint;    // Pointer to the endpoint for the task
    struct Task *next; // Pointer to the next task in the queue
} Task;

// Structure representing a task queue
typedef struct TaskQueue
{
    Task *head;           // Pointer to the head of the task queue
    Task *tail;           // Pointer to the tail of the task queue
    pthread_mutex_t lock; // Mutex for accessing the task queue
} TaskQueue;

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

// Function to write data to a file stream
// Parameters:
//   ptr: Pointer to the data to be written
//   size: Size of each element to be written
//   nmemb: Number of elements to be written
//   stream: File stream to write data into
// Returns:
//   Number of elements successfully written
size_t write_data(void *ptr, size_t size, size_t nmemb, FILE *stream)
{
    size_t written = fwrite(ptr, size, nmemb, stream);
    return written;
}

// Structure representing arguments to be passed to a thread
typedef struct ThreadArguments
{
    TaskQueue *queue;       // Pointer to the task queue
    ThreadControl *control; // Pointer to the thread control structure
} ThreadArguments;

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

    while (queue->head != NULL)
    {
        char *endpoint = (char *)mydequeue(queue); // Dequeue a task from the task queue
        if (endpoint == NULL)
            continue; // Proceed to the next iteration if dequeue returns NULL

        FILE *fp;
        char filename[FILENAME_MAX];
        int currentCount;

        pthread_mutex_lock(&control->count_mutex);
		control->total_calls++;
        currentCount = control->total_calls;
        pthread_mutex_unlock(&control->count_mutex);

        // Generate filename based on the current call count
        sprintf(filename, "/tmp/response_%d.xml", currentCount);
        fp = fopen(filename, "wb");

        if (fp == NULL)
        {
            perror("Cannot open output file");
            return (void *)101; // Return an error code if file opening fails
        }

        CURL *curl = curl_easy_init(); // Initialize a CURL handle
        if (curl)
        {
			char *output = curl_easy_escape(curl, endpoint, strlen(endpoint));
            curl_easy_setopt(curl, CURLOPT_URL, endpoint);
			curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);             // Set the URL to call
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);             // Set the file stream for writing response data
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data); // Set the write function

            increment_calls_this_second(control);   // Increment the call count for the current second
            CURLcode res = curl_easy_perform(curl); // Perform the CURL operation
            if (res != CURLE_OK)
            {
                fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
                fprintf(stderr, "url: %s\n",endpoint);
				curl_easy_cleanup(curl);
                fclose(fp);
                return "done"; // Return an error code if CURL operation fails
            }
            curl_easy_cleanup(curl); // Cleanup the CURL handle
        }
        fclose(fp);     // Close the file stream
        free(endpoint); // Free the memory allocated for the endpoint string
    }
    return NULL; // Return NULL upon successful completion
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
        if (control->terminate_flag)
        {
            pthread_mutex_unlock(&control->mutex);
            break;
        }
        pthread_mutex_unlock(&control->mutex);

        pthread_mutex_lock(&control->calls_mutex);
        control->calls_this_second = 0;
        pthread_cond_signal(&control->can_call);
        pthread_mutex_unlock(&control->calls_mutex);
    }
    return NULL;
}

// Function to get response from API endpoints
// Parameters:
//   self: The Python object
//   args: The arguments passed from Python (expects a list of API endpoints)
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
	pthread_mutex_t my_mutex = PTHREAD_MUTEX_INITIALIZER;
    tqueue->lock = my_mutex;

    size_t queueLen = PyList_Size(listObj);
    for (size_t i = 0; i < queueLen; ++i)
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

    ThreadControl control = {
        .terminate_flag = 0,
        .calls_this_second = 0,
        .total_calls = 0,
        .mutex = PTHREAD_MUTEX_INITIALIZER,
        .calls_mutex = PTHREAD_MUTEX_INITIALIZER,
        .count_mutex = PTHREAD_MUTEX_INITIALIZER,
        .can_call = PTHREAD_COND_INITIALIZER};

    ThreadArguments *targs = malloc(sizeof(ThreadArguments));
	if (!targs)
    {
        PyErr_SetString(PyExc_RuntimeError, "failed to allocate ThreadArguments.");
        return NULL;
    }
	targs->control = &control;
	targs->queue = tqueue;
	

    pthread_t rateLimiterThread;
    pthread_create(&rateLimiterThread, NULL, enforce_call_rate, (void *)&control);

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

    // Wait for all calls to be finished or crash
    for (int i = 0; i < num_threads; i++)
    {
        pthread_join(threads[i], NULL);
    }
    pthread_join(rateLimiterThread, NULL);

    // Clear all allocated variables
    pthread_mutex_destroy(&control.mutex);
    pthread_mutex_destroy(&control.count_mutex);
    pthread_mutex_destroy(&control.calls_mutex);
    pthread_cond_destroy(&control.can_call);
    pthread_mutex_destroy(&tqueue->lock);

    clear_task_queue(tqueue);
    free(tqueue);
	free(targs);
    return Py_BuildValue("s", "done");
}

static PyMethodDef MyApiCallMethods[] = {
    {"get_response",  get_response, METH_VARARGS, "Function to get response from API endpoints."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef myapicallmodule = {
    PyModuleDef_HEAD_INIT,
    "myapicall",   /* name of module */
    NULL,          /* module documentation, may be NULL */
    -1,            /* size of per-interpreter state of the module,
                     or -1 if the module keeps state in global variables. */
    MyApiCallMethods
};

PyMODINIT_FUNC PyInit_myapicall(void) {
    return PyModule_Create(&myapicallmodule);
}