#ifndef XML_UTILS_H
#define XML_UTILS_H

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>

typedef struct {
    const char *prefix;    // Prefix used for the namespace in XPath expressions
    const char *uri;       // URI that defines the namespace
} Namespace;

typedef struct {
    const char *error_code_xpath;
    const char *error_text_xpath;
    char **xpaths;
    char **xmpaths;
    int count;
    int **depthInfo;
    int depthCount;
    Namespace *namespaces;
    int nsCount;
} XPathFields;

int setScopusFieldXPaths(XPathFields *fields); //16
char *safeFetchContent(xmlNode *root, const char *xpath_expr);
char *processMultiField(xmlNode *root, int ival, XPathFields *fields);
int extractAndWriteToCsv(xmlNode *root, FILE *stream, XPathFields *fields);
int parseChunkedXMLResponse(xmlParserCtxtPtr *context,const char *ptr, int size, FILE *stream);
int cleanupXML(xmlParserCtxtPtr *context);

#endif //XML_UTILS_H