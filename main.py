import pandas as pd
from matplotlib import pyplot as plt
from collections import defaultdict #defaults dict entry to 0
from pyvis.network import Network
import math
import random
import atexit
import csv

def goodbye():
    print(header['offset'], entries['count'],searchTerms)
atexit.register(goodbye)



# Initialize
acatFile = pd.read_csv('catNames.csv', encoding ='latin-1')
cKeys = [
    "Code", 
    "Description"
]
tcatFile = pd.read_csv('topCats.csv', encoding='latin-1')
tcKeys = [
    "code", 
    "Description", 
    "Supergroup"
]
journalFile = pd.read_csv('journals.csv', encoding ='latin-1')
jKeys = [
    "Publisher's Name",
    "Publisher imprints grouped to main Publisher",
    "Sourcerecord ID",
    "Source Title",
    "Print-ISSN",
    "E-ISSN",
    "Active or Inactive",
    "Coverage",
    "Article language in source (three-letter ISO language codes)",
    "Medline-sourced Title? (See additional details under separate tab.)",
    "Articles in Press included?",
    "Source Type",
    "Related title 1",
    "Other related title 2",
    "Other related title 3",
    "Other related title 4",
    "All Science Journal Classification Codes (ASJC)"
]

allJournals = {}
# Assuming journalFile is some structure where this operation is valid
for pub, gpub, sid, stit, pissn, eissn, act, cvg, lang, mdl, aip, styp, r1, r2, r3, r4, asjc in zip(*[journalFile[key] for key in jKeys]):
    allJournals[sid] = {
        'stit': stit,
        'pub': pub,
        'gpub': gpub,
        'pissn': pissn,
        'eissn': eissn,
        'act': act,
        'cvg': cvg,
        'lang': lang,
        'mdl': mdl,
        'aip': aip,
        'styp': styp,
        'r1': r1,
        'r2': r2,
        'r3': r3,
        'r4': r4,
        'asjc': asjc,
    }

# General category dictionaries
superCats = defaultdict(int) # All the super groups for categories and their frequencies
for group in tcatFile[tcKeys[2]]: 
    superCats[group] += 1
topCats = {} # All the top level categories and their frequencies
for code, desc in zip(*[tcatFile[key] for key in tcKeys[:2]]):
    topCats[str(code)] = {
        'desc': desc,
        'freq':  0
    }
allCats = {} # All the categories and their codes and frequencies
for code, desc in zip(*[acatFile[key] for key in cKeys]):
    allCats[str(code)] = {
        'desc': desc,
        'freq':  0
    }

# Network Dictionaries for categories
journalCats = defaultdict(int) # The frequency of each # of linked categories for a single journal
catNetEdges = defaultdict(int)

mainCats =  ['11**', '19**', '23**', '31**'] # The main categories pertaining to the climate change topic

for catCodes in journalFile['All Science Journal Classification Codes (ASJC)']:
    delim = '; '
    catCodes = str(catCodes)
    catCodes = catCodes.split(delim)
    journalCats[len(catCodes)] += 1
    for i, code in enumerate(catCodes):
        # Loads the base dictionaries
        if code[:2] != "na":
            allCats[code]['freq'] += 1
            topCats[code[:2]+"**"]['freq'] += 1
            for linkedCode in catCodes[i+1:]:
                if code[:2] != linkedCode[:2] and code[:2] != "na":
                    catNetEdges[(code[:2]+"**", linkedCode[:2]+"**")] += 1

# Bar chart: Displays the information of journalCats
# plt.bar(journalCats.keys(), journalCats.values())
# plt.xlabel('Number of Categories')
# plt.ylabel('Number of Articles')
# plt.title('Frequency of Categories')
# plt.show()# Print the counts for the main categories

# # Bar chart: Displays the information on most common categories
# plt.figure(figsize=(10, 6))  # Adjust figure size as needed
# plt.bar(sorted(topCats.keys()), topCats.values())

# # Spread out the category IDs evenly
# plt.xticks(rotation=45, ha='right')  # Rotating labels for better readability

# plt.xlabel('Category ID')
# plt.ylabel('Number of Articles')
# plt.title('Frequency of Categories')
# plt.tight_layout()  # Adjust layout to prevent clipping of labels
# plt.show()

# Function to generate a random color
# def random_color():
#     return "#{:06x}".format(random.randint(0, 0xFFFFFF))
# # Function to calculate the average color
# def average_color(color1, color2):
#     # Convert hex colors to RGB tuples
#     r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:], 16)
#     r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:], 16)
#     # Calculate average RGB values
#     avg_r = (r1 + r2) // 2
#     avg_g = (g1 + g2) // 2
#     avg_b = (b1 + b2) // 2
#     # Convert average RGB values to hex color
#     return "#{:02x}{:02x}{:02x}".format(avg_r, avg_g, avg_b)

# Prompt user to input top-level categories
# user_input = input("Enter top-level categories (separated by comma), or press Enter to include all: ")
# selected_categories = user_input.split(',') if user_input else list(topCats.keys())

# min_size = 1
# catNet = Network(height="1200px", width="100%", bgcolor="#222222", font_color="white") 
# catNetNodeColor = {}
# for cat in selected_categories:
#     if cat in topCats:
#         catNetNodeColor[cat] = random_color()
#         catNet.add_node(cat, size=min_size + 1 * math.log(topCats[cat] + 1), color=catNetNodeColor[cat],title=str(topCats[cat]))

# catNetMax = max(catNetEdges.values())  # Max amount of connections of a single node (edge weight)
# min_width = 0.1  # Minimum width for edges
# max_width = 10.0  # Maximum width for edges

# for (source, target), count in catNetEdges.items():
#     if source in selected_categories and target in selected_categories:
#         # Scale the edge width logarithmically based on the edge count
#         scaled_width = min_width + (max_width - min_width) * (math.log(count + 1) / math.log(catNetMax + 1))
#         catNet.add_edge(source, target, width=scaled_width,color=[average_color(catNetNodeColor.get(source, '#ffffff'), catNetNodeColor.get(target, '#ffffff'))], title=str(count))


# catNetMax = max(catNetEdges.values()) # Max amount of connections of a single node <=> node
# for (source, target), count in catNetEdges.items():
#     if source in selected_categories and target in selected_categories:
#         catNet.add_edge(source, target, width=.001 + 10 * math.log(count + 1) / math.log(catNetMax + 1), color=average_color(catNetNodeColor.get(source, '#ffffff'), catNetNodeColor.get(target, '#ffffff')), title=str(count))


# Visualize the network graph
# catNet.toggle_physics(False)
# catNet.show('catLinks.html',notebook=False)

import requests
import xml.etree.ElementTree as ET
import sys
import time

def calculate_timeout(n, max_timeout=25):
    base_timeout = 2  
    # Adjust the scale to control how quickly the timeout increases
    scale = 6
    timeout = min(base_timeout + math.log(n + 1) * scale, max_timeout)
    return timeout

def fetch_and_parse_scopus_data(scopus_url, keys):
    headers = {
        'Accept': 'application/xml'
    }
    response = requests.get(scopus_url, headers=headers)
    if response.status_code == 200:
        xml_data = response.text
        return parse_xml(xml_data, keys)
    else:
        print("Error fetching data from Scopus API:",response.status_code)
        return None

def parse_xml(xml_data, keys):
    entries = {}
    entries['entry'] = []
    root = ET.fromstring(xml_data)
    
    # Define namespace map
    namespaces = {
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
        'atom': 'http://www.w3.org/2005/Atom',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
    }
    # Use the namespace map in find/findall functions
    if keys and 'head' in keys:
        entries['count'] = root.find('opensearch:totalResults', namespaces).text
        entries['offset'] = root.find('opensearch:startIndex', namespaces).text
    if keys and 'data' in keys:
        for entry in root.findall('atom:entry', namespaces):
            entry_data = {}
            entry_data['title'] = entry.find('dc:title', namespaces).text
            entry_data['creator'] = entry.find('dc:creator', namespaces).text
            entry_data['publication_name'] = entry.find('prism:publicationName', namespaces).text if entry.find('prism:publicationName', namespaces) is not None else None
            entry_data['volume'] = entry.find('prism:volume', namespaces).text if entry.find('prism:volume', namespaces) is not None else None
            entry_data['issue_identifier'] = entry.find('prism:issueIdentifier', namespaces).text if entry.find('prism:issueIdentifier', namespaces) is not None else None
            entry_data['cover_date'] = entry.find('prism:coverDate', namespaces).text if entry.find('prism:coverDate', namespaces) is not None else None
            entry_data['doi'] = entry.find('prism:doi', namespaces).text if entry.find('prism:doi', namespaces) is not None else None
            entry_data['affiliation'] = entry.find('atom:affiliation/dc:affilname', namespaces).text if entry.find('atom:affiliation/dc:affilname', namespaces) is not None else None
            
            entries['entry'].append(entry_data)
    return entries

# Constructing Scopus API request URL 
scopusKey = "3e98ccbfff5ed19b801086b00dfc5e36"
searchTerms = "climate change global warming"
entries = {
    'offset': 0,
    'count': 0,
    'entry': []
}

filename = searchTerms.replace(" ", "-") + ".csv"
with open(filename, 'w', newline='') as csvfile:
    fn = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    fn.writerow(["ID", "DOI","Title", "Creator", "Publication Name", "Volume", "ISSN", "Cover Date", "Affiliation"])

    # Initial request getting the result information
    scopusReq = f"https://api.elsevier.com/content/search/scopus?query=all({searchTerms})&sort=coverDate&count=25&apiKey={scopusKey}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
    header = fetch_and_parse_scopus_data(scopusReq,['head'])
    if header:
        header['offset'] = int(header['offset'])
        header['count'] = int(header['count'])
        entries['count'] = header['count']
        time.sleep(2)

        while header['offset'] < header['count']:
            
            searchReq = f"https://api.elsevier.com/content/search/scopus?query=all({searchTerms})&start={header['offset']}&sort=coverDate&count=25&apiKey={scopusKey}&view=standard&xml-decode=true&httpAccept=application%2Fxml"
            searchResults = fetch_and_parse_scopus_data(searchReq,['data'])
            if searchResults and 'entry' in searchResults:
                    # entries['entry'].extend(searchResults['entry'])
                    try:
                        fn.writerow(["ID", "DOI","Title", "Creator", "Publication Name", "Volume", "ISSN", "Cover Date", "Affiliation"])
                        fn.writerow(header['offset'], searchResults['doi'],searchResults['title'], searchResults['creator'], 
                                searchResults['publication_name'], searchResults['volume'], searchResults['issue_identifier'],
                                searchResults['cover_data'], searchResults['affiliation'])
                    except Exception:
                        print(Exception)
                        
            else: 
                print(f"Failed to fetch data from Scopus API. (Search attempt on offset: {header['offset']})")
            animation = "|/-\\"
            print(header['offset'],"/",entries['count'],animation[header['offset'] % len(animation)], end = "\r")
            header['offset'] += 25
            

            # Debugging Timeout
            # time.sleep(calculate_timeout(header['offset'] / 25))
            # Runtime Timeout
            time.sleep(.25)
    else:
        print("Failed to fetch initial data from Scopus API.")

print("Done")



