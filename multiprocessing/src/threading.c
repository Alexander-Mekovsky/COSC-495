#include "../include/threading.h"

// Initialize the thread control structure
ThreadControl *controlInit() {
    ThreadControl control = {
        .terminate_flag = 0,
        .terminate_lock = PTHREAD_MUTEX_INITIALIZER,
        .rate = 0,
        .rate_lock = PTHREAD_MUTEX_INITIALIZER,
        .can_run = PTHREAD_COND_INITIALIZER,
        .queued = 0
        .queued_lock = PTHREAD_MUTEX_INTIALIZER};
        return control;
}

// Create a specified number of threads
int *createThreads(pthread_t *threads, pthread_attr_t *attr, void *start_routine, void *args, int count) {
    int res[count];
    for(int i = 0; i < count; ++i){
        res[i] = pthread_create(&threads[i], NULL, start_routine, args) != 0)
    }
    return res;
}

// Join all created threads
int *joinThreads(pthread_t *threads, int count) {
    int res[count];
    for(int i = 0; i < count; ++i){
        res[i] = pthread_join(threads[i], NULL);
    }
    return res;
}

// Check the number of queued tasks
int isQueued(ThreadControl *control) {
    int res;
    pthread_mutex_lock(&control->queued_lock);
    res = control->queued;
    pthread_mutex_unlock(&control->queued_lock);
    return res >= 1;
}

// Increment the number of queued tasks
int incrementQueued(ThreadControl *control) {
    pthread_mutex_lock(&control->queued_lock);
    control->queued++;
    pthread_mutex_unlock(&control->queued_lock);
}
// Decrement the number of queued tasks
int decrementQueued(ThreadControl *control, int rate) {
    pthread_mutex_lock(&control->queued_lock);
    int amount = control->queued;
    if(amount > 0 && amount <= rate)
        control->queued = 0;
    else 
        control->queued = amount - rate;
    pthread_mutex_unlock(&control->queued_lock);
}

// Limit the rate of thread execution
int limitRate(ThreadControl *control, int rate) {
    pthread_mutex_lock(&control->rate_lock);

    while (control->rate >= rate)
    {
        incrementQueued(control);
        pthread_cond_wait(&control->can_run, &control->rate_lock);
    }
    control->rate++;
    pthread_mutex_unlock(&control->rate_lock);
}


// Reset the rate limit
void resetRate(ThreadControl *control, int rate) {
    pthread_mutex_lock(&control->rate_lock);
    control->rate = 0;
    pthread_cond_broadcast(&control->can_run);
    pthread_mutex_unlock(&control->rate_lock);
    decrementQueued(control, rate);
}

// Check if terminate flag is set
int isTerminate(ThreadControl *control) {
    int res;
    pthread_mutex_lock(&control->terminate_lock);
    res = control->terminate_flag;
    pthread_mutex_unlock(&control->terminate_lock);
    return res;
}

// Set the terminate flag
void setTerminate(ThreadControl *control) {
    pthread_mutex_lock(&control->terminate_lock);
    control->terminate_flag = 1;
    pthread_mutex_unlock(&control->terminate_lock);
}

// Clean up the thread control structure
void destroyControl(ThreadControl *control) {
    pthread_mutex_destroy(&control->terminate_lock);
    pthread_mutex_destroy(&control->rate_lock);
    pthread_cond_destroy(&control->can_run);
    pthread_mutex_destroy(&control->queued_lock);
}
