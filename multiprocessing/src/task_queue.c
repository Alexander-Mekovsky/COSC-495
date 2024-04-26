#include "../include/task_queue.h"

// Initialize the task queue
TaskQueue *queueInit() {
    TaskQueue *tqueue = malloc(sizeof(TaskQueue));
    if(!tqueue)
        return NULL;
    tqueue->head = NULL;
    tqueue->tail = NULL;
    pthread_mutex_init(&tqueue->lock,NULL);
    return tqueue;
}

// Check if the queue is empty
int queueIsEmpty(TaskQueue *queue) {
    if(queue->head != NULL)
        return 0;
    return 1;
}

// Dequeue a task from the queue
void *queueDequeue(TaskQueue *queue) {
    pthread_mutex_lock(&queue->lock);

    if (queue->head == NULL) {
        pthread_mutex_unlock(&queue->lock);
        return NULL; 
    }

    Task *temp = queue->head;
    char *data = strdup(temp->endpoint); 
    queue->head = temp->next;

    if (queue->head == NULL)
        queue->tail = NULL;

    free(temp); 
    pthread_mutex_unlock(&queue->lock);
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
TaskQueue *queueFromArr(char **arr, int start, int end) {
    TaskQueue *queue;
    if((queue = queueInit()) == NULL)
        return NULL;
    for(int i = start; i < end; ++i){
        char *point = strdup(arr[i]);
        queueEnqueue(queue,point);
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

        if(temp->endpoint != NULL)
            free(temp->endpoint); // Free the dynamically allocated endpoint string
        free(temp);           // Free the task itself
    }

    queue->tail = NULL;
    pthread_mutex_unlock(&queue->lock);
}

// Destroy the queue and release resources
void queueDestroy(TaskQueue *queue) {
    if (queue != NULL) {
        if (queue->head != NULL)
            queueClear(queue);
        free(queue);
    }
}