#ifndef THREADING_H
#def THREADING_H

#include <stdlib.h>
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
int *createThreads(pthread_t *threads, pthread_attr_t *attr, void *start_routine, void *args, int count);
int *joinThreads(pthread_t *threads, int count);
int limitRate(ThreadControl *control);
void resetRate(ThreadControl *control);
int isTerminate(ThreadControl *control);
void setTerminate(ThreadControl *control);
int isQueued(ThreadControl *control);
int incrementQueued(ThreadControl *control);  
void destroyControl(ThreadControl *control);

#endif THREADING_H