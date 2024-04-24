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

CURLMcode validateMultiHandle(MultiHandle *handle){
    if (handle == NULL || handle->multi_handle == NULL) {
        return CURLM_BAD_HANDLE;
    }
    return CURLM_OK;
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
CURLMcode getMultiInfo(MultiHandle *handle) {
    CURLMcode res;
    if((res = validateMultiHandle(handle)) != CURLM_OK)
        return res;

    CURLMsg *msg;
    int msgs_left = 0;
    pthread_mutex_lock(&handle->lock);
    while((msg = curl_multi_info_read(handle->multi_handle, &msgs_left)) != NULL){
        pthread_mutex_unlock(&handle->lock);

        CURL *easy_handle = msg->easy_handle;
        CURLcode return_code = msg->data.result;

        //fprintf(stderr, "Transfer completed with result %d for handle %p\n", return_code, (void*)easy_handle);
        
        pthread_mutex_lock(&handle->lock);
        curl_multi_remove_handle(handle->multi_handle, easy_handle);
        curlEasyCleanup(easy_handle);
    }
    pthread_mutex_unlock(&handle->lock);
    
    return CURLM_OK;
}

// Clean up libcurl resources
void curlCleanup() {
    curl_global_cleanup();
}

// Clean up an easy handle
void curlEasyCleanup(CURL *easy_handle) {
    if (easy_handle == NULL) {
        return; 
    }

    PrivateHandleData *privateData = NULL;

    curl_easy_getinfo(easy_handle, CURLINFO_PRIVATE, &privateData);

    if (privateData != NULL) {
        free(privateData->url);
        if (privateData->context != NULL) {
            xmlFreeParserCtxt(privateData->context); 
            privateData->context = NULL;
        }
        free(privateData);
        privateData = NULL;
    }

    curl_easy_cleanup(easy_handle);
}

// Clean up a multi handle
void curlMultiCleanup(MultiHandle *handle) {
    CURLMcode res;
    if((res = validateMultiHandle(handle)) != CURLM_OK)
        return res;
    curl_multi_cleanup(handle->multi_handle);
    pthread_mutex_destroy(&handle->lock);
    return res;
}

// Process multi handle actions
CURLMcode processMultiHandle(MultiHandle *handle, int (*check_routine)(void *), void *routine_data) {
    CURLMcode res;
    if((res = validateMultiHandle(handle)) != CURLM_OK)
        return res;

    int still_running = 1; 
    int check_result = 1;

    pthread_mutex_lock(&handle->lock);
    res = curl_multi_perform(handle->multi_handle, &still_running);
    pthread_mutex_unlock(&handle->lock);

    while (still_running || check_result) {
        int numfds;
        
        res = curl_multi_wait(handle->multi_handle, NULL, 0, 1000, &numfds);
        
        if (res != CURLM_OK) {
            return res; 
        }
        if (numfds == 0) {
            usleep(100000);
        }

        pthread_mutex_lock(&handle->lock);
        res = curl_multi_perform(handle->multi_handle, &still_running);
        pthread_mutex_unlock(&handle->lock);

        if (check_routine != NULL) 
            check_result = check_routine(routine_data);
        else 
            check_result = 0;
    }
    }

    res = getMultiInfo(handle);
    return res;
}
