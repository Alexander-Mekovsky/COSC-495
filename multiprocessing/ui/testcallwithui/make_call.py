import pycurl
from urllib.parse import quote
from io import BytesIO
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd
import os 

def read_api_config(api_name):
    api_df = pd.read_csv(os.path.join(r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\api", 'allowedAPI.csv'))
    api_info = api_df.loc[api_df['API'] == api_name]
    
    for api in api_df['API'].values:
        pass
    if not api_info.empty:
        # field_file = api_info.iloc[0]['Field']
        fields_df = pd.read_csv(os.path.join(r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\api",'fields', f"{api_name}.csv"))
        return fields_df
    else:
        return None
    
def read_api_config_two(api_name):
    api_df = pd.read_csv(os.path.join(r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\api", 'allowedAPI.csv'))
    api_info = api_df.loc[api_df['API'] == api_name]

    for api in api_df['API'].values:
        pass
    if not api_info.empty:
        # field_file = api_info.iloc[0]['Field']
        fields_df = pd.read_csv(os.path.join(r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\api",'params', f"{api_name}.csv"))
        return fields_df
    else:
        return None

def validate_fields(fields, fields_df, view):
    valid_fields = []
    clean_fields = []
    for field in fields:
        if field in fields_df['Field'].values:
            if fields_df.loc[fields_df['Field'] == field, view].values[0] == 'X':
                if ':' in field:
                    af = field.split(':')[-1]
                    if af not in clean_fields:
                        clean_fields.append(af)
                elif ' ' in field:
                    wrapper = field.split()[0]
                    if wrapper in fields_df['Field'].values and wrapper not in clean_fields:
                        if ':' in wrapper:
                            aw = field.split(':')[-1]
                            if aw not in clean_fields:
                                clean_fields.append(aw)
                elif field not in clean_fields:
                    clean_fields.append(field)
                
                if field not in valid_fields:
                    valid_fields.append(field)
            else:
                print(f"Removed {field} from the requested fields, it is not available in the {view} view")
        else:
            print(f"Removed {field} from the requested fields, it was not found in the available fields")
    return valid_fields, clean_fields

def fetch_data(api, search_terms, fields, api_key, view='STANDARD', response_type='json', count=25, start=0):
    fields_df = read_api_config(api)
    if fields_df is None:
        print("API not supported.")
        return None, None, None, None
    
    buffer = BytesIO()
    headers = [
        f"Accept: application/{response_type}",
        f"X-ELS-APIKey: {api_key}"
    ]
    
    valid_fields, clean_fields = validate_fields(fields, fields_df, view)
    fields_query = ','.join(clean_fields)
    f = ''
    fields_query = None
    if fields_query is not None:
        f = 'field='
        fields_query = fields_query + "&"
    else:
        fields_query = ''
        
    header_buffer = BytesIO()
    encoded_terms = quote(search_terms)  # URL encode the search terms
    query = f"https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY({encoded_terms})&{f}{fields_query}count={count}&start={start}&view={view}"

    c = pycurl.Curl()
    c.setopt(c.URL, query)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HEADERFUNCTION, header_buffer.write)
    c.perform()
    c.close()

    # Parse response headers
    header_info = parse_headers(header_buffer.getvalue().decode('utf-8'))
    reset_timestamp = int(header_info.get('X-RateLimit-Reset', 0))
    remaining_queries = int(header_info.get('X-RateLimit-Remaining', 0))
    reset_time = datetime.utcfromtimestamp(reset_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC') if reset_timestamp else "Unavailable"

    # Parse response body
    response = buffer.getvalue().decode('utf-8')
    if 'application/json' in header_info.get('Content-Type', ''):
        return parse_json(response, 'data', valid_fields), header_info, reset_time, remaining_queries
    else:
        return parse_xml(response, 'data', valid_fields), header_info, reset_time, remaining_queries

def parse_headers(response):
    headers = {}
    for line in response.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def get_text_from_element(parent, tag, namespaces, default=''):
    """
    Helper function to extract text safely from an XML element.
    
    Args:
        parent (ET.Element): Parent element to search within.
        tag (str): Tag to search for within the parent.
        namespaces (dict): Dictionary of XML namespaces.
        default (str): Default value if the tag is not found or has no text.
        
    Returns:
        str: Text content of the found element, or default value.
    """
    element = parent.find(tag, namespaces)
    return element.text if element is not None and element.text is not None else default


# def parse_xml(xml_data, data_type):
#     """
#     Parse XML data and extract relevant information.

#     Args:
#         xml_data (str): XML data to be parsed.
#         data_type (str): Type of data to parse ('head' or 'data').

#     Returns:
#         dict or int: Parsed data if data_type is 'data', total results count if data_type is 'head',
#             or 2 if an invalid data_type is provided.
#     """
#     # Namespace map for finding elements within the XML structure.
#     NAMESPACES = {
#         'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
#         'atom': 'http://www.w3.org/2005/Atom',
#         'dc': 'http://purl.org/dc/elements/1.1/',
#         'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
#     }

#     # print(xml_file)
#     entries = {'entry': []}
#     if data_type == 'head':
#         root = ET.fromstring(xml_data)
#     else:
#         root = ET.fromstring(xml_data)  # Use parse() to read from a file
    
#     if data_type == 'head':
#         return root.find('opensearch:totalResults', NAMESPACES).text
#     elif data_type == 'data':
#         for entry in root.findall('atom:entry', NAMESPACES):
#             entry_data = {
#                 'id': get_text_from_element(entry, 'dc:identifier', NAMESPACES)[10:],  # Remove the prefix if present
#                 'source_id': get_text_from_element(entry, 'atom:source-id', NAMESPACES),
#                 'issn': get_text_from_element(entry, 'prism:issn', NAMESPACES),
#                 'eissn': get_text_from_element(entry, 'prism:eIssn', NAMESPACES),
#                 'isbn': get_text_from_element(entry, 'prism:isbn', NAMESPACES),
#                 'title': get_text_from_element(entry, 'dc:title', NAMESPACES),
#                 'creator': get_text_from_element(entry, 'dc:creator', NAMESPACES),
#                 'publication_name': get_text_from_element(entry, 'prism:publicationName', NAMESPACES),
#                 'cover_date': get_text_from_element(entry, 'prism:coverDate', NAMESPACES),
#                 'cited_by': get_text_from_element(entry, 'atom:citedby-count', NAMESPACES),
#                 'type': get_text_from_element(entry, 'prism:aggregationType', NAMESPACES),
#                 'subtype': get_text_from_element(entry, 'atom:subtypeDescription', NAMESPACES),
#                 'article_number': get_text_from_element(entry, 'atom:article-number', NAMESPACES),
#                 'volume': get_text_from_element(entry, 'prism:volume', NAMESPACES),
#                 'doi': get_text_from_element(entry, 'prism:doi', NAMESPACES)
#             }
#             # Handling affiliations as before or using the helper function if needed
#             entries['entry'].append(entry_data)
            
#             # Handling multiple affiliations
#             affiliations = []
#             for affiliation in entry.findall('atom:affiliation', NAMESPACES):
#                 affilname = affiliation.find('atom:affilname', NAMESPACES)
#                 affilcity = affiliation.find('atom:affiliation-city', NAMESPACES)
#                 affilcountry = affiliation.find('atom:affiliation-country', NAMESPACES)
                
#                 affil_parts = []
#                 if affilname is not None and affilname.text is not None:
#                     affil_parts.append(affilname.text)
#                 if affilcity is not None and affilcity.text is not None:
#                     affil_parts.append(affilcity.text)
#                 if affilcountry is not None and affilcountry.text is not None:
#                     affil_parts.append(affilcountry.text)

#                 affiliations.append('-'.join(affil_parts))
            
#             entry_data['affiliation'] = 'x'.join(affiliations)

#             entries['entry'].append(entry_data)
#         return entries
#     else:
#         print("Error: no valid types")
#         return 2

def parse_xml(xml_data, data_type, valid_fields):
    """
    Parse XML data and extract relevant information based on the specified valid fields.

    Args:
        xml_data (str): XML data to be parsed.
        data_type (str): Type of data to parse ('head' or 'data').
        valid_fields (list): List of valid fields to parse.
        fields_df (DataFrame): DataFrame containing field definitions.

    Returns:
        dict: Parsed data if data_type is 'data', or an error message.
    """
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',  # Default namespace (no prefix)
        'dc': 'http://purl.org/dc/elements/1.1/',
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
    }

    root = ET.fromstring(xml_data)
    entries = {'entry': []}

    print(xml_data)
    print(valid_fields)
    
    if data_type == 'data':
        for entry in root.findall('.//atom:entry', NAMESPACES):
            entry_data = {}
            for field in valid_fields:
                if "ref=" in field:  # Handling elements with specific ref attributes
                    attr, value = field.split("=")
                    ref_element = entry.find(f".//atom:link[@ref='{value}']", NAMESPACES)
                    if ref_element is not None:
                        entry_data[f"{value}-ref"] = ref_element.get('href', 'N/A')
                elif ' ' in field:  # Handling wrapped fields
                    wrapper, subfield = field.split(' ', 1)
                    
                    if wrapper not in entry_data:
                        entry_data[wrapper] = ''
                        
                    wrapped_elements = entry.findall(f".//atom:{wrapper}//atom:{subfield}", NAMESPACES)
                    if wrapped_elements:
                        for elem in wrapped_elements:
                            if entry_data[wrapper] != '':
                                entry_data[wrapper] = entry_data[wrapper][:-1]
                            entry_data[wrapper] = entry_data[wrapper] + (elem.text.strip() if elem.text else '') + '-='
                else:
                    ns, tag = field.split(':') if ':' in field else ('atom', field)
                    ns_xpath = f"{ns}:"
                    xpath_query = f".//{ns_xpath}{tag}"
                    entry_data[tag] = get_text_from_element(entry, xpath_query, NAMESPACES)
            for field in entry_data:
                if entry_data[field][-2:] == '-=':
                    entry_data[field] = entry_data[field][:-2]
            entries['entry'].append(entry_data)
        return entries
    else:
        return "Error: Invalid data type or no data section provided"

def parse_json(json_data, data_type, valid_fields):
    """
    Parse JSON data and extract detailed information based on the specified valid fields.

    Args:
        json_data (str): JSON string to be parsed.
        data_type (str): Type of data to parse ('head' or 'data').
        valid_fields (list): List of valid fields to parse.
        fields_df (DataFrame): DataFrame containing field definitions.

    Returns:
        dict: Parsed data if data_type is 'data', or an error message.
    """
    data = json.loads(json_data)
    print(data)
    entries = {'entry': []}

    if data_type == 'data':
        for entry in data.get('search-results', {}).get('entry', []):
            entry_data = {}
            for field in valid_fields:
                if ' ' in field:  # Handling nested fields like 'affiliation affilname'
                    wrapper, subfield = field.split(' ', 1)
                    nested_value = entry.get(wrapper, {})
                    entry_data[subfield] = nested_value.get(subfield, 'N/A')
                else:
                    entry_data[field.split(':')[-1]] = entry.get(field, 'N/A')
            entries['entry'].append(entry_data)
        return entries
    else:
        return "Error: Invalid data type or no data section provided"


def print_entries(data):
    # Check if 'entry' key exists and iterate over its list of entries
    if 'entry' in data:
        for i, entry in enumerate(data['entry'], 1):
            print(f"Entry {i}:")
            for key, value in entry.items():
                # Nicely format the key to remove namespaces for better readability
                formatted_key = key.split(':')[-1]  # Splitting on ':' and taking the last part for display
                print(f"  {formatted_key}: {value}")
            print("-" * 60)  # Separator for entries
        

def make_basic_call(api,link):
    pass

def make_call(api_key, search_terms, response_type, api, fields, view):
    count = 1
    start = 0
    results, headers, reset_time, remaining = fetch_data(api,search_terms,fields, api_key,view, response_type, count, start)
    if results is not None:
        print("Quota remaining:", remaining)
        print("Quota resets at:", reset_time)
        print_entries(results)
