#include "../include/task_queue.h"

// Initialize the task queue
int queueInit(TaskQueue *queue) {
    if(!(TaskQueue *tqueue = malloc(sizeof(TaskQueue))))
        return 1;
    tqueue->head = NULL;
    tqueue->tail = NULL;
    pthread_mutex_t qlock = PTHREAD_MUTEX_INITIALIZER;
    tqueue->lock = qlock;
    return 0;
}

// Check if the queue is empty
int queueIsEmpty(TaskQueue *queue) {
    if(queue->head != queue)
        return 0;
    return 1;
}

// Dequeue a task from the queue
void *queueDequeue(TaskQueue *queue) {
    pthread_mutex_lock(&queue->lock);

    if (queue->head == NULL)
    {
        pthread_mutex_unlock(&queue->lock);
        return NULL; // Queue is empty, return NULL
    }

    Task *temp = queue->head;
    char *data = strdup(temp->endpoint); // Duplicate the string to return a valid pointer
    queue->head = queue->head->next;

    if (queue->head == NULL)
    {
        queue->tail = NULL;
    }

    pthread_mutex_unlock(&queue->lock);
    free(temp->endpoint);
    free(temp);
    return data;
}

// Enqueue a task to the queue
void queueEnqueue(TaskQueue *queue, char *endpoint) {
    Task *task = malloc(sizeof(Task));
    task->endpoint = endpoint;
    task->next = NULL;

    pthread_mutex_lock(&queue->lock);

    if (queue->tail == NULL)
    {
        queue->head = queue->tail = task;
    }
    else
    {
        queue->tail->next = task;
        queue->tail = task;
    }

    pthread_mutex_unlock(&queue->lock);
}

// Create a task queue from an array
TaskQueue *queueFromArr(void *arr, int start, int end) {
    TaskQueue *queue;
    if(queueInit(&queue) != 0)
        return NULL;
    for(int i = start; i < end; ++i){
        queueEnqueue(queue,arr[i]);
    }
    return queue;
    
}

// Clear all tasks from the queue
void queueClear(TaskQueue *queue) {
    pthread_mutex_lock(&queue->lock);

    while (queue->head != NULL)
    {
        Task *temp = queue->head;
        queue->head = queue->head->next;

        free(temp->endpoint); // Free the dynamically allocated endpoint string
        free(temp);           // Free the task itself
    }

    queue->tail = NULL;
    pthread_mutex_unlock(&queue->lock);
}

// Destroy the queue and release resources
void queueDestroy(TaskQueue *queue) {
    if(queue->head != NULL)
        queueClear(queue);
    free(queue);
}