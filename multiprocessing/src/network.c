#include "../include/network.h"

// Report easy handle errors
const char *easyError(CURLcode code) {
    return curl_easy_strerror(code);
}

// Report multi handle errors
const char *multiError(CURLMcode code) {
    return curl_multi_strerror(code);
}

// Initialize libcurl
CURLcode curlInit() {
    return curl_global_init(CURL_GLOBAL_ALL);
}

// Initialize an easy handle
CURL *curlEasyInit() {
    return curl_easy_init();
}

// Initialize a multi handle
MultiHandle *curlMultiInit() {
    MultiHandle handle = {
        .multi_handle = curl_multi_init(),
        .lock = PTHREAD_MUTEX_INITIALIZER
    };
    return handle;
}

// Set options for an easy handle
CURLcode *setEasyOptions(CURL *easy_handle, Option *options, int count) {
    CURLcode res[count];
    for(int i = 0; i < count; ++i){
        res[i] = curl_easy_setopt(easy_handle, options[i]->option, options[i]->parameter);
    }
    return res;
}

// Set options for a multi handle
CURLMcode *setMultiOptions(MultiHandle *handle, Option *options, int count) {
    CURLMcode res[count];
    for(int i = 0; i < count; ++i){
        res[i] = curl_multi_setopt(handle->multi_handle, options[i]->moption, options[i]->parameter);
    }
    return res;
}

// Attach private data to an easy handle
CURLcode setPrivateData(CURL *easy_handle, PrivateHandleData *data) {
    return curl_easy_setopt(easy_handle, CURLINFO_PRIVATE, data)
}

// Set callback functions for an easy handle
CURLcode setEasyCallBack(CURL *easy_handle, void *callback, void *args) {
    CURLcode res;
    if ((res = curl_easy_setopt(easy_handle, CURLOPT_WRITEFUNCTION, callback)) != 0)
        return res;
    res = curl_easy_setopt(easy_handle, CURLOPT_WRITEDATA, args);
    return res;
}

// Add an easy handle to a multi handle
CURLMcode addMultiHandle(MultiHandle *handle, CURL *easy_handle) {
    CURLMcode res;
    pthread_mutex_lock(&handle->lock);
    res = curl_multi_add_handle(handle->multi_handle, easy_handle);
    pthread_mutex_unlock(&handle->lock);
    return res;
}

// Retrieve private data from an easy handle
CURLcode getPrivateData(CURL *easy_handle, PrivateHandleData *data) {
    return curl_easy_getinfo(easy_handle, CURLINFO_PRIVATE, &data);
}

// Retrieve information about an easy handle
CURLcode getEasyInfo(CURL *easy_handle, Option *options) {
    CURLcode res;
    res = curl_easy_getinfo(easy_handle, options->option, &options->parameter);
    return res;
}

// Retrieve information about a multi handle
CURLMcode getMultiInfo(MultiHandle *handle, Option *option) {
    CURLMcode res;
    pthread_mutex_lock(&handle->lock);
    res = curl_easy_getinfo(handle->multi_handle, options->option, &options->parameter);
    pthread_mutex_unlock(&handle->lock);
    return res;
}

// Clean up libcurl resources
void curlCleanup() {
    curl_global_cleanup();
}

// Clean up an easy handle
void curlEasyCleanup(CURL *easy_handle) {
    curl_easy_cleanup(easy_handle);
}

// Clean up a multi handle
void curlMultiCleanup(MultiHandle *handle) {
    curl_multi_cleanup(handle->multi_handle);
    pthread_mutex_destroy(&handle->lock);
}

// Process multi handle actions
CURLMcode processMultiHandle(MultiHandle *handle) {
    // Function implementation
}
