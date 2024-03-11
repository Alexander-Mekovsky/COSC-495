import requests
import math
import xml.etree.ElementTree as ET
import sys
import time
import csv
import numpy as np
import statistics

def calculate_timeout(n, max_timeout=25):
    """
    Calculate a dynamic timeout based on the number of requests made.

    Parameters:
    - n (int): The number of requests that have been made.
    - max_timeout (int): The maximum allowed timeout value. Default is 25 seconds.

    Returns:
    - float: A calculated timeout value to be used between API requests.
    """
    base_timeout = 2  # Initial timeout value in seconds.
    scale = 6  # Adjusts how quickly the timeout value increases.
    timeout = min(base_timeout + math.log(n + 1) * scale, max_timeout)
    return timeout

def parse_xml(xml_data, keys):
    """
    Parse the XML data from the Scopus API response.

    Parameters:
    - xml_data (str): XML data as a string from the API response.
    - keys (list): A list of strings indicating which parts of the data to parse ('head' for metadata, 'data' for entry data).

    Returns:
    - dict: A dictionary containing the parsed XML data.
    """
    start_timer3 = time.time()
    entries = {'entry': []}
    root = ET.fromstring(xml_data)
    
    # Namespace map for finding elements within the XML structure.
    namespaces = {
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
        'atom': 'http://www.w3.org/2005/Atom',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
    }

    if keys and 'head' in keys:
        entries['count'] = root.find('opensearch:totalResults', namespaces).text
        entries['offset'] = root.find('opensearch:startIndex', namespaces).text
    if keys and 'data' in keys:
        for entry in root.findall('atom:entry', namespaces):
            entry_data = {}
            # Correctly extracting specific elements from each entry, if available.
            entry_data['id'] = entry.find('dc:identifier', namespaces).text[10:]
            entry_data['source_id'] = entry.find('atom:source-id', namespaces).text
            entry_data['issn'] = entry.find('prism:issn', namespaces).text if entry.find('prism:issn', namespaces) is not None else ''
            entry_data['eissn'] = entry.find('prism:eIssn', namespaces).text if entry.find('prism:eIssn', namespaces) is not None else ''
            entry_data['isbn'] = entry.find('prism:isbn', namespaces).text if entry.find('prism:isbn', namespaces) is not None else ''
            entry_data['title'] = entry.find('dc:title', namespaces).text
            entry_data['creator'] = entry.find('dc:creator', namespaces).text if entry.find('dc:creator', namespaces) is not None else ''
            entry_data['publication_name'] = entry.find('prism:publicationName', namespaces).text 
            entry_data['cover_date'] = entry.find('prism:coverDate', namespaces).text
            entry_data['cited_by'] = entry.find('atom:citedby-count', namespaces).text
            entry_data['type'] = entry.find('prism:aggregationType', namespaces).text
            entry_data['subtype'] = entry.find('atom:subtypeDescription', namespaces).text
            entry_data['article_number'] = entry.find('atom:article-number', namespaces).text if entry.find('atom:article-number', namespaces) is not None else ''
            entry_data['volume'] = entry.find('prism:volume', namespaces).text if entry.find('prism:volume', namespaces) is not None else ''
            entry_data['doi'] = entry.find('prism:doi', namespaces).text if entry.find('prism:doi', namespaces) is not None else ''
            if entry.findall('atom:affiliation',namespaces) is not None:
                for affiliation in entry.findall('atom:affiliation',namespaces):
                    affilname = affiliation.find('atom:affilname',namespaces)
                    affilcity = affiliation.find('atom:affiliation-city',namespaces)
                    affilcountry = affiliation.find('atom:affiliation-country',namespaces)
                    
                    entry_data['affiliation'] = ''
                    if affilname is not None and affilname.text is not None:
                        entry_data['affiliation'] += affilname.text + "-"
                    if affilcity is not None and affilcity.text is not None:
                        entry_data['affiliation'] += affilcity.text + "-"
                    if affilcountry is not None and affilcountry.text is not None:
                        entry_data['affiliation'] += affilcountry.text + "x"

            entries['entry'].append(entry_data)
    end_timer3 = time.time()
    return entries, end_timer3 - start_timer3


def fetch_and_parse_scopus_data(scopus_url, keys):
    """
    Fetch and parse data from the Scopus API.

    Parameters:
    - scopus_url (str): The URL for the Scopus API request.
    - keys (list): A list of strings indicating which parts of the data to parse.

    Returns:
    - dict: A dictionary containing parsed XML data or None if an error occurs.
    """
    headers = {
        'Accept': 'application/xml'
    }
    start_timer2 = time.time()
    response = requests.get(scopus_url, headers=headers)
    if response.status_code == 200:
        xml_data = response.text
        end_timer2 = time.time()
        return parse_xml(xml_data, keys), end_timer2 - start_timer2
    else:
        print("Error fetching data from Scopus API:", response.status_code)
        return None

def index_scopus_response(key, terms):
    """
    Fetch and index Scopus API responses based on search terms.

    Parameters:
    - key (str): The API key for Scopus.
    - terms (str): The search terms.

    Returns:
    - str: A status message indicating whether the indexing was successful or not.
    """
    start_time = time.time()
    timer2 = []
    timer3 = []
    timer4 = []
    entries = {'offset': 0, 'count': 0, 'entry': []}
    filename = terms.replace(" ", "-") + ".csv"
    with open(filename, 'w', newline='', encoding='utf-8', errors='replace') as file:
        wr = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wr.writerow(["Scopus ID", "Source ID", "ISSN(IA)","eISSN(IA)","ISBN(IA)", "Title", "Creator", "Publication Name", "Cover Date","Cited by #", "Type", "Subtype","Article number (IA)", "Volume(IA)","DOI(IA)","Affiliation(IA)"])
        
        # Initial request to get total count of results.
        headerReq = f"https://api.elsevier.com/content/search/scopus?query=all({terms})&sort=coverDate&count=0&apiKey={key}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
        header, time2 = fetch_and_parse_scopus_data(headerReq, ['head'])
        header, time3 = header
        timer2.append(time2)
        timer3.append(time3)
        if header:
            header['offset'] = 0
            header['count'] = int(header['count'])
            entries['count'] = header['count']
            # time.sleep(5)
            
            while header['offset'] < header['count']:
                dataReq = f"https://api.elsevier.com/content/search/scopus?query=all({terms})&start={header['offset']}&sort=coverDate&count=25&apiKey={key}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
                data, time2 = fetch_and_parse_scopus_data(dataReq, ['data'])
                data, time3 = data
                timer2.append(time2)
                timer3.append(time3)
                start_time4 = time.time()
                if data and len(data['entry']) != 0:
                    entries['entry'].extend(data['entry'])
                    try:
                        for result in data['entry']:
                            # Write parsed data into the CSV file.
                            wr.writerow([result.get('id'), result.get('source_id'), result.get('issn'), 
                                         result.get('eissn'), result.get('isbn'),
                                         result.get('title'), result.get('creator'), result.get('publication_name'),
                                         result.get('cover_date'), result.get('cited_by'), result.get('type'),
                                         result.get('subtype'), result.get('article_number'), result.get('volume'), 
                                         result.get('doi'), result.get('affiliation')])
                            animation = "|/-\\"
                            print(header['offset'], "/", entries['count'], animation[header['offset'] % len(animation)], end="\r")
                            header['offset'] += 1
                    except Exception as e:
                        print("Error: ", e)
                else: 
                    print(f"Failed to fetch data from Scopus API. (Search attempt on offset: {header['offset']})")
                # time.sleep(0.25)
                # time.sleep(calculate_timeout(header['offset'] / 25))
                end_timer4 = time.time()
                timer4.append(end_timer4-start_time4)
        else:
            return "Failed to fetch initial data from Scopus API."
    end_time = time.time()
    out = result = """\
        For {count} results it took {time} seconds...

        Averages:
        API REQUEST TIME: {req_avg} seconds on {req_count} attempts
            Max: {req_max} seconds
            Min: {req_min} seconds
            Median: {req_median}
            Mode: {req_mode}
            Std. Dev.: {req_std_dev}

        API RESPONSE PARSE TIME: {parse_avg} seconds on {parse_count} attempts
            Max: {parse_max} seconds
            Min: {parse_min} seconds
            Median: {parse_median}
            Mode: {parse_mode}
            Std. Dev.: {parse_std_dev}

        WRITE PARSED: {write_avg} seconds on {write_count} attempts
            Max: {write_max} seconds
            Min: {write_min} seconds
            Median: {write_median}
            Mode: {write_mode}
            Std. Dev.: {write_std_dev}
        """.format(
            count=header['count'],
            time=end_time - start_time,
            req_avg=sum(timer2) / len(timer2),
            req_count=len(timer2),
            req_max=np.max(timer2),
            req_min=np.min(timer2),
            req_median=np.median(timer2),
            req_mode=statistics.mode(timer2),
            req_std_dev=np.std(timer2),
            parse_avg=sum(timer3) / len(timer3),
            parse_count=len(timer3),
            parse_max=np.max(timer3),
            parse_min=np.min(timer3),
            parse_median=np.median(timer3),
            parse_mode=statistics.mode(timer3),
            parse_std_dev=np.std(timer3),
            write_avg=sum(timer4) / len(timer4),
            write_count=len(timer4),
            write_max=np.max(timer4),
            write_min=np.min(timer4),
            write_median=np.median(timer4),
            write_mode=statistics.mode(timer4),
            write_std_dev=np.std(timer4)
        )


    return out