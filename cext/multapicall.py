import xml.etree.ElementTree as ET
# import math
# import sys
import csv
import numpy as np
# import statistics
import myapicall
import os
import threading
import requests
import time


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

    entries = {'entry': []}
    root = ET.fromstring(xml_file)  # Use parse() to read from a file
    
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


caller_finished_event = threading.Event()
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

    # Compiles a list of API calls
    while offset < total:
        url = f"https://api.elsevier.com/content/search/scopus?query=all({terms})&sort=coverDate&start={offset}&count={nResults}&apiKey={key}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
        url = url.replace(" ", "%20")
        urls.append(url)
        offset += increment

    # Make concurrent API calls
    starttime = time.time()
    result = myapicall.get_response(urls)
    endtime = time.time()
    print(endtime-starttime, " seconds\n")
    # Set event flag if all API calls are completed
    if result == "done":
        caller_finished_event.set()
        return True
    else:
        print("Error making API calls:", result)
        return False

def any_file_of_format(directory, file_format):
    """
    Checks if any file in the directory ends with the specified format.

    Args:
        directory (str): Directory path to search for files.
        file_format (str): File format to check for.

    Returns:
        bool: True if at least one file with the specified format is found, False otherwise.
    """
    try:
        return any(file.endswith(file_format) for file in os.listdir(directory))
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        return False
    except Exception as e:
        print(f"Error occurred while checking file format: {e}")
        return False

def write_csv(data, terms):
    """
    Writes parsed data into a CSV file.

    Args:
        data (dict): Parsed data entries.
        terms (str): Search terms used for parsing.

    Returns:
        int: Status code indicating success (0) or failure (1).
    """
    filename = terms.replace(" ", "-") + ".csv"
    try:
        with open(filename, 'w', newline='', encoding='utf-8', errors='replace') as file:
            wr = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            wr.writerow(["Scopus ID", "Source ID", "ISSN(IA)","eISSN(IA)","ISBN(IA)", "Title", "Creator", "Publication Name", "Cover Date","Cited by #", "Type", "Subtype","Article number (IA)", "Volume(IA)","DOI(IA)","Affiliation(IA)"])

            for result in data['entry']:
                wr.writerow([result.get('id'), result.get('source_id'), result.get('issn'), 
                             result.get('eissn'), result.get('isbn'),
                             result.get('title'), result.get('creator'), result.get('publication_name'),
                             result.get('cover_date'), result.get('cited_by'), result.get('type'),
                             result.get('subtype'), result.get('article_number'), result.get('volume'), 
                             result.get('doi'), result.get('affiliation')])
        return 0
    except Exception as e:
        print(f"Error occurred while writing to CSV file: {e}")
        return 3

def parser(terms, total):
    """
    Parses XML files and writes the parsed data into a CSV file.

    Args:
        terms (str): Search terms used for parsing.
        total (int): Total number of results to parse.
    """
    offset = 0
    while not caller_finished_event.is_set() and not any_file_of_format("/tmp",".xml"):
        xml_file_path = next((file for file in os.listdir('/tmp') if file.endswith('.xml')), None)
        if not os.path.exists(f"/tmp/{xml_file_path}"):
            print("Error: File path error")
        while os.path.getsize(f"/tmp/{xml_file_path}") == 0:
            time.sleep(1)

        data = parse_xml(f"/tmp/{xml_file_path}")
        os.remove(f"/tmp/{xml_file_path}")
        if data and len(data['entry']) != 0:
            status_code = write_csv(data, terms)
            if status_code != 0:
                return status_code
            offset += len(data['entry'])
        else: 
            print(f"Failed to fetch data from Scopus API. (Search attempt on offset: {offset})")
    return 0

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
        
        # Sleep for 1 second to avoid overwhelming the API
        time.sleep(1)
        
        # Multithreading calls
        caller_thread = threading.Thread(target=caller, args=(terms, key, total, increment), name="CallerThread")
        parser_thread = threading.Thread(target=parser, args=(terms, total), name="ParserThread")
        
        # Start the threads
        caller_thread.start()
        parser_thread.start()

        # Wait for the threads to complete
        caller_thread.join()
        parser_thread.join()
        
    else:
        print(f"ERROR: Initial header request for search terms '{terms}' has been unsuccessful (RESPONSE_CODE: {response.status_code})")
        return 1

def main():
    scopus_key = "3e98ccbfff5ed19b801086b00dfc5e36"
    search_terms = "climate change global warming ocean atmosphere moon"
    res = process_scopus_data(search_terms, scopus_key)
    print(res)
if __name__ == "__main__":
    main()