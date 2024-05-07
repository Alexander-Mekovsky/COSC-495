#include "../include/curl_utils.h"

CURLcode curlInit(){
    return curl_global_init(CURL_GLOBAL_ALL);
}
void cleanupCurl(){
    curl_global_cleanup();
}

CURL *easyInit(){
    return curl_easy_init();
}
const char *easyError(CURLcode code){
    return curl_easy_strerror(code);
}
CURLcode getEasyPrivate(CURL *easy_handle, PrivateHandleData *data){
    return curl_easy_getinfo(easy_handle, CURLINFO_PRIVATE, data);
}
void cleanupEasy(CURL *easy_handle){
    if (easy_handle == NULL) return; 
    
    PrivateHandleData *privateData = NULL;

    getEasyPrivate(easy_handle, privateData);

    if (privateData != NULL) {
        free(privateData->url);
        if(privateData->stream) {
            fclose(privateData->stream);
            privateData->stream = NULL;
        }
        privateData->stream = NULL;
        free(privateData);
        privateData = NULL;
    }

    curl_easy_cleanup(easy_handle);
}

MultiHandle *multiInit(){
    MultiHandle *handle = (MultiHandle *) malloc(sizeof(MultiHandle));
    if(!handle) return NULL;
    
    handle->multi_handle = curl_multi_init();
    pthread_mutex_init(&handle->lock, NULL);
    // handle->can_perform = 1;
    // pthread_mutex_init(&handle->control_lock,NULL);

    return handle;
}
const char *multiError(CURLMcode code){
    return curl_multi_strerror(code);
}
CURLMcode validateMulti(MultiHandle *handle){
    if(handle == NULL)  
        return CURLM_BAD_HANDLE;
    if(handle->multi_handle == NULL)
        return CURLM_BAD_HANDLE;
    return CURLM_OK;
}
CURLMcode addMultiEasy(MultiHandle *handle, CURL *easy_handle){
    CURLMcode res;
    pthread_mutex_lock(&handle->lock);
    res = curl_multi_add_handle(handle->multi_handle, easy_handle);
    pthread_mutex_unlock(&handle->lock);
    return res;
}
CURLMcode rmvMultiEasy(MultiHandle *handle, CURL *easy_handle){
    if(validateMulti(handle) != CURLM_OK) 
        return CURLM_BAD_HANDLE;
    if(easy_handle == NULL) 
        return CURLM_BAD_EASY_HANDLE;

    CURLMcode res;
    pthread_mutex_lock(&handle->lock);
    res = curl_multi_remove_handle(handle->multi_handle, easy_handle);
    pthread_mutex_unlock(&handle->lock);
    cleanupEasy(easy_handle);
    return res;
}
CURLMcode wakeupMulti(MultiHandle *handle){
    pthread_mutex_lock(&handle->lock);
    CURLMcode res = curl_multi_wakeup(handle->multi_handle);
    pthread_mutex_unlock(&handle->lock);
    return res;
}
CURLMcode performMulti(MultiHandle *handle, int (*check_routine)(void *), void *check_data){
    CURLMcode res = CURLM_OK;

    int still_running = 0; 
    int check_result = 0;
    int numfds = 0;
    do{
        pthread_mutex_lock(&handle->lock);
        int pres = curl_multi_perform(handle->multi_handle, &still_running);
        pthread_mutex_unlock(&handle->lock);

        if(pres != CURLM_OK){
            return pres;
        }

        int wres = curl_multi_poll(handle->multi_handle, NULL, 0, 1000, &numfds);
        if(wres != CURLM_OK){
            return wres;
        }

        if (check_routine != NULL) 
            check_result = check_routine(check_data);
        else 
            check_result = numfds;

        if (numfds == 0) {
            usleep(100000);
        }
    } while (still_running || check_result);
    
    return res;
}
int completeMultiTransfers(MultiHandle *handle, FILE *log_file, int log_out, FILE *out_file, int (*check_routine)(void *), void *check_data,int (*parse_write_routine)(void *), void *parse_data){
    
    if(validateMulti(handle) != CURLM_OK)
        return 1;

    CURLMsg *msg;
    int msgs_left = 0;
    int check_result = 1;
    
    while(check_result){ 
        pthread_mutex_lock(&handle->lock);
        while((msg = curl_multi_info_read(handle->multi_handle, &msgs_left)) != NULL){
            pthread_mutex_unlock(&handle->lock);

            CURL *easy_handle = msg->easy_handle;
            CURLcode return_code = msg->data.result; // for log file
            fprintf(stderr, "Res: %s\n", easyError(return_code));
            //fprintf(stderr, "Transfer completed with result %d for handle %p\n", return_code, (void*)easy_handle);
            PrivateHandleData *pdata = NULL;
            curl_easy_getinfo(easy_handle, CURLINFO_PRIVATE, &pdata);
            if(pdata == NULL){
                fprintf(stderr, "ERROR on PDATA");
                rmvMultiEasy(handle, easy_handle);
                pthread_mutex_lock(&handle->lock);
                continue;
            }
            if(pdata->stream){
                fclose(pdata->stream);
                pdata->stream = NULL;
            }

            // if(parse_write_routine != NULL){
                // ParseParameters *params = malloc(sizeof(ParseParameters));
                // params->filename = data->filename;
                // params->outfile = out_file;
                // params->parse_args = parse_data;
                
                // gettimeofday(&data->parse_start, NULL);
                // parse_write_routine((void *)params);
                // gettimeofday(&data->parse_end, NULL);
            // }
            
            if(log_out){
                float req_time = 0.0, parse_time = 0.0;
                if(pdata->req_start.tv_sec != -1 && pdata->req_start.tv_usec != -1 && pdata->req_end.tv_sec != -1 && pdata->req_end.tv_usec != -1) {
                    req_time = (pdata->req_end.tv_sec - pdata->req_start.tv_sec) + (pdata->req_end.tv_usec - pdata->req_start.tv_usec) / 1e6;
                    if (pdata->req_end.tv_usec < pdata->req_start.tv_usec) {
                        req_time -= 1;  // Adjust the second down
                        req_time += (1e6 + pdata->req_end.tv_usec - pdata->req_start.tv_usec) / 1e6;  // Add the correct microsecond fraction
                    }
                }

                if(pdata->parse_start.tv_sec != -1 && pdata->parse_start.tv_usec != -1 && pdata->parse_end.tv_sec != -1 && pdata->parse_end.tv_usec != -1) {
                    parse_time = (pdata->parse_end.tv_sec - pdata->parse_start.tv_sec) + (pdata->parse_end.tv_usec - pdata->parse_start.tv_usec) / 1e6;
                    if (pdata->parse_end.tv_usec < pdata->parse_start.tv_usec) {
                        parse_time -= 1;  // Adjust the second down
                        parse_time += (1e6 + pdata->parse_end.tv_usec - pdata->parse_start.tv_usec) / 1e6;  // Add the correct microsecond fraction
                    }
                }

                fprintf(log_file, "%s,%f,%f\n", pdata->url, req_time, parse_time);
            }
            if(rmvMultiEasy(handle, easy_handle) != CURLM_OK)
                return 2;

            if (check_routine != NULL) 
                check_result = check_routine(check_data);
            else 
                check_result = msgs_left;
            pthread_mutex_lock(&handle->lock);
        }
        pthread_mutex_unlock(&handle->lock);
    }

    return 0;
}
void cleanupMulti(MultiHandle *handle){
    if((validateMulti(handle)) != CURLM_OK) return;

    curl_multi_cleanup(handle->multi_handle);
    pthread_mutex_destroy(&handle->lock);
    free(handle);
    handle = NULL;
}