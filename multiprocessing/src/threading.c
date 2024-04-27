#include "../include/threading.h"

// Initialize the thread control structure
ThreadControl *controlInit() {
    ThreadControl *control = malloc(sizeof(ThreadControl));
    if(!control) return NULL;

    control->terminate_flag = 0;
    control->rate = 0;
    control->queued = 0;
    pthread_mutex_init(&control->terminate_lock, NULL);
    pthread_mutex_init(&control->rate_lock, NULL);
    pthread_mutex_init(&control->queued_lock, NULL);
    pthread_cond_init(&control->can_run,NULL);

    return control;
}

// Create a specified number of threads
int createThreads(pthread_t *threads, pthread_attr_t *attr, void * (*start_routine)(void *), void *args, int count) {
    int res = 0;
    for(int i = 0; i < count; ++i){
        if (pthread_create(&threads[i], attr, start_routine, args) != 0)
            res = 1;
    }
    return res;
}

// Join all created threads
int joinThreads(pthread_t *threads, int count) {
    int res = 0;
    for(int i = 0; i < count; ++i){
        if (pthread_join(threads[i], NULL) != 0)
            res = 1;
    }
    return res;
}

// Check the number of queued tasks
int isQueued(void *args) {
    ThreadControl *control = (ThreadControl *)args;
    int res;
    pthread_mutex_lock(&control->queued_lock);
    res = control->queued;
    pthread_mutex_unlock(&control->queued_lock);
    return res >= 1;
}

// Increment the number of queued tasks
int incrementQueued(ThreadControl *control) {
    pthread_mutex_lock(&control->queued_lock);
    int qc = control->queued++;
    pthread_mutex_unlock(&control->queued_lock);
    return qc; 
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
    return amount;
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
    struct timeval tv;
    gettimeofday(&tv, NULL);
    int hours = (tv.tv_sec / 3600) % 24; // Convert seconds to hours
    int minutes = (tv.tv_sec / 60) % 60; // Convert seconds to minutes
    int seconds = tv.tv_sec % 60; // Seconds
    int milliseconds = tv.tv_usec / 1000; // Convert microseconds to milliseconds

    // Log the current time and rate
    fprintf(stderr, "%02d:%02d:%02d:%03d - Calls this second is - %d\n",
            hours, minutes, seconds, milliseconds, control->rate);
    return 0;
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
    free(control);
}
