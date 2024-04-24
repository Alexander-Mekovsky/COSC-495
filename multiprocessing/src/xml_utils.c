#include "../include/xml_utils.h"

// Implementations of the functions declared in xml_utils.h
int setScopusFieldXPaths(XPathFields *fields) {
    if (fields == NULL){
        return -1;
    }

    static Namespace namespaces[] = {
        {"atom", "http://www.w3.org/2005/Atom"}
    };
    fields->namespaces = namespaces;
    fields->nsCount = sizeof(namespaces) / sizeof(namespaces[0]);

    fields->error_code_xpath = "//status/statusCode";
    fields->error_text_xpath = "//status/statusText";
    fields->count = 16;
    fields->depthCount = 1;
    fields->depthInfo = {{15, 0, 2, 3}}; // i val, namespace i, depth level, depth count

    static char *paths[fields->count] = {
        "//dc:identifier",
        "//atom:source-id",
        "//prism:issn",
        "//prism:eIssn",
        "//prism:isbn",
        "//dc:title",
        "//dc:creator",
        "//prism:publicationName",
        "//prism:coverDate",
        "//atom:citedby-count",
        "//prism:aggregationType",
        "//atom:subtypeDescription",
        "//prism:articleNumber",
        "//prism:volume",
        "//prism:doi",
        "//prism:affiliation"
    };
    fields->xpaths = paths;
    static char *mpaths[3] = {
        "atom:affilname",
        "atom:affiliation-city",
        "atom:affiliation-country"
    };
    fields->xmpaths = mpaths;

    return 0;
}

char *safeFetchContent(xmlNode *root, const char *xpath_expr) {
    if(root == NULL || xpath_expr == NULL) return NULL;
    xmlXPathContextPtr context = xmlXPathNewContext(root->doc);
    
    if(context == NULL) return NULL;
    xmlXPathObjectPtr result = xmlXPathEvalExpression((xmlChar *)xpath_expr, context);
    char *content = "";

    if (result != NULL && result->nodesetval != NULL && result->nodesetval->nodeNr > 0) {
        content = (char *)xmlNodeGetContent(result->nodesetval->nodeTab[0]);
    }

    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
    return content;
}


char *processMultiField(xmlNode *root, int ival, XPathFields *fields) {
    if (fields == NULL){
        return -1;
    }
    xmlXPathContextPtr context = xmlXPathNewContext(root->doc);
    
    int ns = fields->depthInfo[i][1];
    xmlXPathRegisterNs(context, (xmlChar *)fields->namespaces[ns][0], (xmlChar *)fields->namespaces[ns][1]);
    xmlXPathObjectPtr result = xmlXPathEvalExpression((xmlChar *)fields->xpath[i], context);
    
    int off = 0;
    if (i != 0){
        off = fields->depthInfo[i-1][3];
    }

    char multi[4096] = "";
    if (result != NULL && result->nodesetval != NULL) {
        for (int j = 0; j < result->nodesetval->nodeNr; j++) {
            char multiParts[1024] = "";
            
            snprintf(multiParts, sizeof(multiParts), "%s-%s-%s",
                    (char *)xmlNodeGetContent(xmlXPathEvalExpression((xmlChar *)fields->xmpath[0+off], context)->nodesetval->nodeTab[j]),
                    (char *)xmlNodeGetContent(xmlXPathEvalExpression((xmlChar *)fields->xmpath[1+off], context)->nodesetval->nodeTab[j]),
                    (char *)xmlNodeGetContent(xmlXPathEvalExpression((xmlChar *)fields->xmpath[2+off], context)->nodesetval->nodeTab[j]));
            strcat(multi, multiParts);
            
            if (i < result->nodesetval->nodeNr - 1) {
                strcat(multi, "|");
            }
        }
    }

    xmlXPathFreeObject(result);
    xmlXPathFreeContext(context);
    return multi;
}


int extractAndWriteToCsv(xmlNode *root, FILE *stream) {
    XPathFields *fields;
    if(setScopusFieldXPaths(&fields)< 0)
        return -1;
    int len = fields->count;
    int off = len - fields->countMulti;

    // if(safeFetchContent(root,fields->error_code_xpath) != "" || safeFetchContent(root, fields->error_text_xpath) != "")
    //     return -2;

    for(int i = 0; i < len; ++i){
        fprintf(stream, "\"%s\"", safeFetchContent(root,fields->xpaths[i]));
        if(i >= off)
            fprintf(stream, "\"%s\"", processMultiField(root,i,fields);
    }

    fprintf(stream, "\n");

    return 0;
}

int parseChunkedXMLResponse(xmlParserCtxtPtr *context, const char *ptr, int size, FILE *stream) {
    if (context == NULL || *context == NULL || ptr == NULL) return -1;

    size_t real_size = size * nmemb;
    int lastChunk = 0;
    if (xmlParseChunk(context, ptr, real_size, lastChunk)) {
        if (DEBUG == 1 )
            fprintf(stderr, "Error while parsing XML chunk\n");
        return -1;
    }

    int res;
    if (lastChunk) {
        xmlNode *root_element = xmlDocGetRootElement(context->myDoc);
        if (root_element) {
            res = extractAndWriteToCsv(root_element, stream);
        }
        close(stream);
        cleanupXML(context);
    }
    if (res < 0)
        return res;

    return lastChunk; 
}


int cleanupXML(xmlParserCtxtPtr *context) {
    if(context != NULL && *context != NULL) {
        xmlFreeDoc((*context)->myDoc);
        xmlFreeParserCtxt(*context);
        *context = NULL;
    }

    return 0;
}