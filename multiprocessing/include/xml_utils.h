#ifndef XML_UTILS_H
#define XML_UTILS_H

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include <string.h>
#include <stdio.h>

typedef struct Namespace{
    const char *prefix;    // Prefix used for the namespace in XPath expressions
    const char *uri;       // URI that defines the namespace
} Namespace;

typedef struct {
    const char *error_code_xpath;
    const char *error_text_xpath;
    char **xpaths;
    char **xmpaths;
    int count;
    int (*depthInfo)[4];
    int depthCount;
    Namespace *namespaces;
    int nsCount;
} XPathFields;

typedef struct {
    char *filename;
    FILE *parsefile;
    FILE *outfile; 
    XPathFields *parse_args;
} ParseArguments;

int checkXPathErrorCode(xmlNode *root, XPathFields *fields);
int setScopusFieldXPaths(XPathFields *fields); //16
char *safeFetchContent(xmlNode *root, const char *xpath_expr);
void processMultiField(xmlNode *root, int ival, XPathFields *fields, char *multi, size_t multiSize);
int extractAndWriteToCsv(xmlNode *root, FILE *stream, XPathFields *fields);
int parseChunkedXMLResponse(xmlParserCtxtPtr context,const char *ptr, int size, FILE *stream, XPathFields *fields);
void cleanupXPathFields(XPathFields *fields);
int cleanupXML(xmlParserCtxtPtr context);
int readCallback(void *context, char *buffer, int len);
int closeCallback(void *context);
int parseXMLFile(void *args);

#endif //XML_UTILS_H