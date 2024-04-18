#ifndef NETWORK_H
#define NETWORK_H

// Required Uses
#include <curl/curl.h>

// Optional Uses
#include <stdlib.h>
#include <pthread.h>
#include "threading.h"
#include <libxml/parser.h>

typedef struct {
    CURLoption option;
    CURLMoption moption;
    void *parameter;
} Option;

typedef struct {
    CURLM *multi_handle;
    pthread_mutex lock;
} MultiHandle;

typedef struct {
    char *url;
    xmlParserCtxtPtr context;
    struct timeval req_start;
    struct timeval req_end;
    struct timeval parse_start;
    struct timeval parse_end;
} PrivateHandleData;

const char *easyError(CURLcode code);
const char *multiError(CURLMcode code);

CURLcode curlInit();
CURL *easyInit();
MultiHandle *multiInit();
CURLcode setEasyOptions(CURL *easy_handle, Option *options);
CURLMcode setMultiOptions(MultiHandle *handle, Option *options);
CURLcode setPrivateData(CURL *easy_handle, PrivateHandleData *data);
CURLcode setEasyCallBack(CURL *easy_handle, void *callback, void *args);
CURLMcode addMultiHandle(MultiHandle *handle, CURL easy_handle);
CURLcode getPrivateData(CURL *easy_handle, PrivateHandleData *data);
CURLcode getEasyInfo(CURL *easy_handle, Option *option);
CURLMcode getMultiInfo(MultiHandle *handle, Option *option);
void curlCleanup();
void curlEasyCleanup();
void curlMultiCleanup();
CURLMcode processMultiHandle(MultiHandle *handle);

#endif NETWORK_H