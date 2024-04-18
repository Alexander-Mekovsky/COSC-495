#ifndef XML_UTILS_H
#define XML_UTILS_H

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>

typedef struct {
    const char *error_code_xpath;
    const char *error_text_xpath;
    char **xpaths;
    int count;
} XPathFields;

int setScopusFieldXPaths(XPathFields *fields, char *api); //16
char *fetchContent(xmlNode *root, const char *xpath_expr);
void scopusAffiliation(xmlNode *root, char *buffer);
int extractAndWriteToCsv(xmlNode *root, FILE *stream);
int parseChunkedXMLResponse(xmlParserCtxtPtr *context, int size, FILE *stream);
int cleanupXML(xmlParserCtxtPtr *context);

#endif XML_UTILS_H