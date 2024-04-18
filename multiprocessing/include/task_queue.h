#ifndef TASK_QUEUE_H
#define TASK_QUEUE_H

#include <stdlib.h>
#include <pthread.h>

typedef struct {
    char *endpoint;
    struct Task *next;
} Task;

typedef struct {
    Task *head;
    Task *tail;
    pthread_mutex_t lock;
} TaskQueue;

TaskQueue *queueInit();
TaskQueue *queueFromArr(void *arr, int start, int end);
int queueIsEmpty(TaskQueue *queue);
void *queueDequeue(TaskQueue *queue);
void queueEnqueue(TaskQueue *queue);
int queueClear(TaskQueue *queue);
int queueDestroy(TaskQueue *queue);

#endif TASK_QUEUE_H