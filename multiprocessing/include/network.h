#ifndef NETWORK_H
#define NETWORK_H

#include <curl/curl.h>
#include <pthread.h>
#include <libxml/parser.h>

typedef struct {
    CURLoption option;
    void *parameter;
} Option;

typedef struct {
    CURLM *multi_handle;
    pthread_mutex_t lock;
} MultiHandle;

typedef struct {
    char *url;
    xmlParserCtxtPtr context;
    struct timeval start;
    struct timeval end;
} PrivateHandleData;

void initializeCurl();

CURL *createEasyHandle(char *url, Option **options);
MultiHandle *createMultiHandle(Option **options);

void getPrivateData(CURL *handle, void *data);

void addMultiHandle(CURLM *multi_handle, CURL *easy_handle);

void setEasyCallBack(void *func, void *data);
CURLMcode processMultiHandle(CURLM *handle, void option);

void cleanupMultiHandle(CURLM *handle);
void cleanupEasyHandle(CURL *handle);
void cleanupCurl();

#endif NETWORK_H