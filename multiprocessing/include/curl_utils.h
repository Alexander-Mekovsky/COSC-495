#ifndef NETWORK_H
#define NETWORK_H

// Required Uses
#include <curl/curl.h>

// Optional Uses
#include <stdlib.h>
#include <stdio.h>
#include <sys/time.h>
#include <pthread.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/time.h>

typedef struct {
    CURLM *multi_handle;
    pthread_mutex_t lock;
} MultiHandle;

typedef struct {
    int firstChunk;
    char *url;
    FILE *stream;
    struct timeval req_start;
    struct timeval req_end;
    struct timeval parse_start;
    struct timeval parse_end;
} PrivateHandleData;

typedef struct {
    char *filename;
    FILE *outfile; 
    void *parse_args;
} ParseParameters;


CURLcode curlInit();
void cleanupCurl();

CURL *easyInit();
const char *easyError(CURLcode code);
CURLcode getEasyPrivate(CURL *easy_handle, PrivateHandleData *data);
void cleanupEasy(CURL *easy_handle);

MultiHandle *multiInit();
const char *multiError(CURLMcode code);
CURLMcode validateMulti(MultiHandle *handle);
CURLMcode addMultiEasy(MultiHandle *handle, CURL *easy_handle);
CURLMcode rmvMultiEasy(MultiHandle *handle, CURL *easy_handle);
CURLMcode wakeupMulti(MultiHandle *handle);
CURLMcode performMulti(MultiHandle *handle, int (*check_routine)(void *), void *routine_data);
CURLMcode completeMultiTransfers(MultiHandle *handle, FILE *log_file, int log_out, FILE *stream, int (*check_routine)(void *), void *check_data,int (*parse_write_routine)(void *), void *parse_data);
void cleanupMulti(MultiHandle *handle);

#endif //NETWORK_H