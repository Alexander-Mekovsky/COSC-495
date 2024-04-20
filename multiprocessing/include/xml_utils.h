#ifndef XML_UTILS_H
#define XML_UTILS_H

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>

typedef struct {
    const char *error_code_xpath;
    const char *error_text_xpath;
    char **xpaths;
    char **xmpaths;
    int count;
    int countMulti;
    int *multiDepth;
} XPathFields;

int setScopusFieldXPaths(XPathFields *fields); //16
char *safeFetchContent(xmlNode *root, const char *xpath_expr);
void processMultiField(xmlNode *root, char *fields, char *buffer);
int extractAndWriteToCsv(xmlNode *root, FILE *stream, XPathFields *fields);
int parseChunkedXMLResponse(xmlParserCtxtPtr *context, int size, FILE *stream);
int cleanupXML(xmlParserCtxtPtr *context);

#endif XML_UTILS_H