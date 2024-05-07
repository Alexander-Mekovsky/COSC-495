#ifndef TASK_QUEUE_H
#define TASK_QUEUE_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>

typedef struct Task{
    char *endpoint;
    struct Task *next;
} Task;

typedef struct TaskQueue{
    Task *head;
    Task *tail;
    pthread_mutex_t lock;
} TaskQueue;

TaskQueue *queueInit();
TaskQueue *queueFromArr(char **arr, int start, int end);
int queueIsEmpty(TaskQueue *queue);
void *queueDequeue(TaskQueue *queue);
void queueEnqueue(TaskQueue *queue, char *endpoint);
void queueClear(TaskQueue *queue);
void queueDestroy(TaskQueue *queue);

#endif //TASK_QUEUE_H