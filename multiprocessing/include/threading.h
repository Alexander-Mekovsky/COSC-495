#ifndef THREADING_H
#define THREADING_H

#include <stdlib.h>
#include <stdio.h>
#include <sys/time.h>
#include <string.h>
#include <pthread.h>

typedef struct {
    int terminate_flag;
    pthread_mutex_t terminate_lock;
    int rate;
    pthread_mutex_t rate_lock;
    pthread_cond_t can_run;
    int queued;
    pthread_mutex_t queued_lock;
} ThreadControl;

ThreadControl *controlInit();
int createThreads(pthread_t *threads, pthread_attr_t *attr, void * (*start_routine)(void *), void *args, int count);
int joinThreads(pthread_t *threads, int count);
int incrementQueued(ThreadControl *control);
int decrementQueued(ThreadControl *control, int rate);
int limitRate(ThreadControl *control, int rate);
void resetRate(ThreadControl *control, int rate);
int isTerminate(void *args);
void setTerminate(ThreadControl *control);
int isQueued(void *args);
void cleanupControl(ThreadControl *control);

#endif //THREADING_H