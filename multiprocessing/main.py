import xml.etree.ElementTree as ET
# import math
# import sys
import csv
import numpy as np
# import statistics
import myapicall
import os
import requests
import time
from path import Path


def parse_xml(xml_file, data_type):
    """
    Parse XML data and extract relevant information.

    Args:
        xml_data (str): XML data to be parsed.
        data_type (str): Type of data to parse ('head' or 'data').

    Returns:
        dict or int: Parsed data if data_type is 'data', total results count if data_type is 'head',
            or 2 if an invalid data_type is provided.
    """
    # Namespace map for finding elements within the XML structure.
    NAMESPACES = {
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
        'atom': 'http://www.w3.org/2005/Atom',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
    }

    # print(xml_file)
    entries = {'entry': []}
    if data_type == 'head':
        root = ET.fromstring(xml_file)
    else:
        root = ET.parse(xml_file)  # Use parse() to read from a file
    
    if data_type == 'head':
        return root.find('opensearch:totalResults', NAMESPACES).text
    elif data_type == 'data':
        for entry in root.findall('atom:entry', NAMESPACES):
            entry_data = {}
            entry_data['id'] = entry.find('dc:identifier', NAMESPACES).text[10:]
            entry_data['source_id'] = entry.find('atom:source-id', NAMESPACES).text
            entry_data['issn'] = entry.find('prism:issn', NAMESPACES).text if entry.find('prism:issn', NAMESPACES) is not None else ''
            entry_data['eissn'] = entry.find('prism:eIssn', NAMESPACES).text if entry.find('prism:eIssn', NAMESPACES) is not None else ''
            entry_data['isbn'] = entry.find('prism:isbn', NAMESPACES).text if entry.find('prism:isbn', NAMESPACES) is not None else ''
            entry_data['title'] = entry.find('dc:title', NAMESPACES).text
            entry_data['creator'] = entry.find('dc:creator', NAMESPACES).text if entry.find('dc:creator', NAMESPACES) is not None else ''
            entry_data['publication_name'] = entry.find('prism:publicationName', NAMESPACES).text 
            entry_data['cover_date'] = entry.find('prism:coverDate', NAMESPACES).text
            entry_data['cited_by'] = entry.find('atom:citedby-count', NAMESPACES).text
            entry_data['type'] = entry.find('prism:aggregationType', NAMESPACES).text
            entry_data['subtype'] = entry.find('atom:subtypeDescription', NAMESPACES).text
            entry_data['article_number'] = entry.find('atom:article-number', NAMESPACES).text if entry.find('atom:article-number', NAMESPACES) is not None else ''
            entry_data['volume'] = entry.find('prism:volume', NAMESPACES).text if entry.find('prism:volume', NAMESPACES) is not None else ''
            entry_data['doi'] = entry.find('prism:doi', NAMESPACES).text if entry.find('prism:doi', NAMESPACES) is not None else ''
            
            # Handling multiple affiliations
            affiliations = []
            for affiliation in entry.findall('atom:affiliation', NAMESPACES):
                affilname = affiliation.find('atom:affilname', NAMESPACES)
                affilcity = affiliation.find('atom:affiliation-city', NAMESPACES)
                affilcountry = affiliation.find('atom:affiliation-country', NAMESPACES)
                
                affil_parts = []
                if affilname is not None and affilname.text is not None:
                    affil_parts.append(affilname.text)
                if affilcity is not None and affilcity.text is not None:
                    affil_parts.append(affilcity.text)
                if affilcountry is not None and affilcountry.text is not None:
                    affil_parts.append(affilcountry.text)

                affiliations.append('-'.join(affil_parts))
            
            entry_data['affiliation'] = 'x'.join(affiliations)

            entries['entry'].append(entry_data)
        return entries
    else:
        print("Error: no valid types")
        return 2


def caller(terms, key, total, increment):
    """
    Initiates API calls to fetch data from the Scopus API and sets an event flag upon completion.

    Args:
        terms (str): Search terms to query the Scopus API.
        key (str): API key for accessing the Scopus API.
        total (int): Total number of results to fetch.
        increment (int): Number of results to fetch per API call.

    Returns:
        bool: True if all API calls are completed successfully, False otherwise.
    """
    nResults = 25
    offset = 0
    urls = []
    urls.append(f"testing.csv")

    # Compiles a list of API calls
    while offset < total and offset < 5000:
        url = f"https://api.elsevier.com/content/search/scopus?query=all({terms})&sort=coverDate&start={offset}&count={nResults}&apiKey={key}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
        url = url.replace(" ", "%20")
        urls.append(url)
        offset += increment

    # Make concurrent API calls
    starttime = time.time()
    result = myapicall.get_response(urls)
    endtime = time.time()
    print(endtime-starttime, " seconds\n")
    # Expected value = 2212.5
    # Set event flag if all API calls are completed
    if result == "done":
        return True
    else:
        print("Error making API calls:", result)
        return False

def process_scopus_data(terms, key, increment=25, start=0):
    """
    Fetches data from the Scopus API, initiates multithreading for processing,
    and waits for the threads to complete.

    Args:
        key (str): API key for accessing the Scopus API.
        terms (str): Search terms to query the Scopus API.
        increment (int): Number of results to fetch per API call (default is 25).
        start (int): Offset for starting the search results (default is 0).

    Returns:
        int: Status code indicating success (0) or failure (1).
    """
    offset = start
    nResults = 0
    API_BASE_URL = f"https://api.elsevier.com/content/search/scopus?query=all({terms})&sort=coverDate&start={offset}&count={nResults}&apiKey={key}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
    HEADERS = {'Accept': 'application/xml'}

    
    response = requests.get(API_BASE_URL, headers=HEADERS)
    
    if response.status_code == 200:       
        xml = response.text
        total = int(parse_xml(xml, 'head'))
        print(total)
        # Sleep for 1 second to avoid overwhelming the API
        time.sleep(1)
        
        caller(terms,key,total,increment)
        #parser(terms,total)
    else:
        print(f"ERROR: Initial header request for search terms '{terms}' has been unsuccessful (RESPONSE_CODE: {response.status_code})")
        return 1

def main():
    # 5335658c3e71c91bed47e6a055f22a6
    scopus_key = "3e98ccbfff5ed19b801086b00dfc5e36"
    search_terms = "climate change global warming ocean atmosphere" 
    # ocean atmosphere moon star
    res = process_scopus_data(search_terms, scopus_key)
    print(res)
if __name__ == "__main__":
    main()