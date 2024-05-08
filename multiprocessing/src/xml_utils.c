#include "../include/xml_utils.h"

int checkXPathErrorCode(xmlNode *root, XPathFields *fields){
    if (fields == NULL) return -1;

    char *statusCode = safeFetchContent(root, fields->error_code_xpath);
    char *statusText = safeFetchContent(root, fields->error_text_xpath);

    if ((statusCode && strcmp(statusCode, "") != 0) || (statusText && strcmp(statusText, "") != 0)) {
        return atoi(statusCode);
    }

    if (statusCode) free(statusCode);
    if (statusText) free(statusText);
    return 0;
}

// Implementations of the functions declared in xml_utils.h
int setScopusFieldXPaths(XPathFields *fields) {
    if (fields == NULL) {
        return -1;
    }

    static struct Namespace namespaces[] = {
        {"atom", "http://www.w3.org/2005/Atom"},
        {"dc", "http://purl.org/dc/elements/1.1/"},
        {"prism", "http://prismstandard.org/namespaces/basic/2.0/"}
    };
    fields->namespaces = namespaces;
    fields->nsCount = 1;

    fields->error_code_xpath = "//status/statusCode";
    fields->error_text_xpath = "//status/statusText";
    fields->error_response_type = "json";

    fields->count = 16;
    fields->depthCount = 1;

    static int depthInfo[1][4] = {
        {15, 0, 2, 3}  // i value, namespace i, depth level, depth count
    };
    fields->depthInfo = depthInfo;
    
    static char *paths[16] = {
        "//dc:identifier", "//atom:source-id", "//prism:issn", "//prism:eIssn",
        "//prism:isbn", "//dc:title", "//dc:creator", "//prism:publicationName",
        "//prism:coverDate", "//atom:citedby-count", "//prism:aggregationType",
        "//atom:subtypeDescription", "//atom:articleNumber", "//prism:volume",
        "//prism:doi", "//atom:affiliation"
    };
    fields->xpaths = paths;

    static char *mpaths[3] = {
        "atom:affilname", "atom:affiliation-city", "atom:affiliation-country"
    };
    fields->xmpaths = mpaths;

    return 0; // Success
}

char *safeFetchContent(xmlNode *root, const char *xpath_expr) {
    if (root == NULL || xpath_expr == NULL) return NULL;
    
    xmlXPathContextPtr context = xmlXPathNewContext(root->doc);
    if (context == NULL) return NULL;
    
    xmlXPathObjectPtr result = xmlXPathEvalExpression((xmlChar *)xpath_expr, context);
    char *content = NULL;  

    if (result != NULL && result->nodesetval != NULL && result->nodesetval->nodeNr > 0) {
        xmlChar *nodeContent = xmlNodeGetContent(result->nodesetval->nodeTab[0]);
        if (nodeContent != NULL) {
            content = strdup((char *)nodeContent);
            xmlFree(nodeContent);  
        }
    }

    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
    return content; 
}


void processMultiField(xmlNode *root, int ival, XPathFields *fields, char *multi, size_t multiSize) {
    if (fields == NULL || root == NULL || root->doc == NULL || multi == NULL) return; 
    
    xmlXPathContextPtr context = xmlXPathNewContext(root->doc);
    if (context == NULL) return; 

    int ns = fields->depthInfo[ival][1];
    if (xmlXPathRegisterNs(context, (xmlChar *)fields->namespaces[ns].prefix, (xmlChar *)fields->namespaces[ns].uri) != 0) {
        xmlXPathFreeContext(context);
        return;  // Namespace registration failed
    }
    
    xmlXPathObjectPtr result = xmlXPathEvalExpression((xmlChar *)fields->xpaths[ival], context);
    
    multi[0] = '\0';
    if (result != NULL && result->nodesetval != NULL && result->nodesetval->nodeNr > 0) {
        size_t currentLength = 0;
        for (int j = 0; j < result->nodesetval->nodeNr; j++) {
            xmlXPathObjectPtr partResults[3];
            for (int k = 0; k < 3; k++) {
                partResults[k] = xmlXPathEvalExpression((xmlChar *)fields->xmpaths[k + fields->depthInfo[ival][3]], context);
            }
            
            char multiParts[1024] = ""; // consider dynamic allocation
            int written = snprintf(multiParts, sizeof(multiParts), "%s-%s-%s",
                (char *)xmlNodeGetContent(partResults[0]->nodesetval->nodeTab[j]),
                (char *)xmlNodeGetContent(partResults[1]->nodesetval->nodeTab[j]),
                (char *)xmlNodeGetContent(partResults[2]->nodesetval->nodeTab[j]));
            for (int k = 0; k < 3; k++) {
                xmlXPathFreeObject(partResults[k]);
            }
            
            if (written > 0 && (currentLength + written + 1) < multiSize) { 
                if (currentLength > 0) {
                    strncat(multi, "|", multiSize - currentLength - 1); 
                    currentLength++;
                }
                strncat(multi, multiParts, multiSize - currentLength - 1);
                currentLength += written;
            }
        }
    }

    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
}




int extractAndWriteToCsv(xmlNode *root, FILE *stream, XPathFields *fields) {
    if (root == NULL || stream == NULL || fields == NULL) {
        return -1;  // Error code for invalid input
    }

    int len = fields->count;
    int off = len - fields->depthCount;
    char multiFieldResult[4096];
    char *content = NULL;

    for (int i = 0; i < len; ++i) {
        if(i < off){
            content = safeFetchContent(root, fields->xpaths[i]);
            if (content != NULL) {
                fprintf(stream, "\"%s\"", content);
                free(content); 
            } else {
                fprintf(stream, "\"\"");
            }
        } else {
            int j;
            for (j = 0; j < fields->depthCount; ++j) {
                if (fields->depthInfo[j][0] == i) {
                    break;
                }
            }
            processMultiField(root, j, fields, multiFieldResult, sizeof(multiFieldResult));
            fprintf(stream, ",\"%s\"", multiFieldResult);
        }
        if(i+1 < len) fprintf(stream, ",");
    }

    fprintf(stream, "\n");
    return 0;
}

int parseChunkedXMLResponse(xmlParserCtxtPtr context, const char *ptr, int size, FILE *stream, XPathFields *fields) {
    if (context == NULL || ptr == NULL) return -1;

    int lastChunk = 0;
    if (xmlParseChunk(context, ptr, size, lastChunk)) {
        return 0;
    }

    int res = -1;
    if (lastChunk) {
        xmlNode *root_element = xmlDocGetRootElement(context->myDoc);
        if (root_element) {
            res = extractAndWriteToCsv(root_element, stream, fields);
        }
        cleanupXML(context);
    }
    if (res < 0)
        return 0;

    return lastChunk; 
}

char getFirstChar(const char* filename) {
    FILE *file;
    char firstChar = '\0';  // Default to null character if reading fails

    file = fopen(filename, "r");  // Open the file for reading
    if (file == NULL) {
        perror("Error opening file");
        return firstChar;  // Return null character if file cannot be opened
    }

    // Read the first character
    int result = fgetc(file);
    if (result != EOF) {
        firstChar = (char)result;
    } else {
        perror("Error reading character");
    }

    // Close the file
    fclose(file);

    return firstChar;
}

int parseXMLFile(void *args) {
    ParseArguments *pargs = (ParseArguments *)args;
    if ((char)getFirstChar(pargs->filename) == '{')
        return 301;
    xmlDocPtr doc = xmlReadFile(pargs->filename, NULL, 0);
    if (!doc) return -1;  // Error loading file

    xmlNode *root_element = xmlDocGetRootElement(doc);
    if (!root_element) {
        xmlFreeDoc(doc);
        return -1;
    }

    int res = extractAndWriteToCsv(root_element, pargs->outfile, pargs->parse_args);
    xmlFreeDoc(doc);
    free(pargs);
    return res;
}

void cleanupXPathFields(XPathFields *fields) {
    if (fields == NULL) return;
    free(fields);
    fields = NULL;
}

int cleanupXML(xmlParserCtxtPtr context) {
    if(context != NULL) {
        xmlFreeDoc(context->myDoc);
        xmlFreeParserCtxt(context);
        context = NULL;
    }

    return 0;
}