import pandas as pd
from matplotlib import pyplot as plt
from collections import defaultdict #defaults dict entry to 0
from pyvis.network import Network
import math
import random

# Initialize
catNames = pd.read_csv('catNames.csv', encoding ='latin-1')
cKeys = [
    "code", 
    "Description"
]
topNames = pd.read_csv('topCats.csv', encoding='latin-1')
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
    
print(allJournals[21100447128])
#     allJournals[journal] = {}
    
# basic Journal format
# 
# publishername = {sourcetitle,sourcerecordid, sourcetype, issn, eissn, coverage, ajsc}


#journalFile['All Science Journal Classification Codes (ASJC)']:


# General category dictionaries
superCats = defaultdict(int) # All the super groups for categories and their frequencies
topCats = {} # All the top level categories and their frequencies
# topCats = {code = {name = exname, freq = freq}}
allCats = {} # All the categories and their codes and frequencies
# allCats = {code = {name = exname, freq = freq}}





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
            allCats[code] += 1
            topCats[code[:2]+"**"] += 1
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

def fetch_scopus_data(scopus_url):
    headers = {
        'Accept': 'application/xml'
    }
    response = requests.get(scopus_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("Error fetching data from Scopus API.")
        return None

def parse_xml(xml_data):
    entries = {}
    entries['entry'] = []
    root = ET.fromstring(xml_data)
    
    entries['count'] = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text
    entries['offset'] = root.find('{http://a9.com/-/spec/opensearch/1.1/}startIndex').text
    
    print(entries['count'])
    print(entries['offset'])
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        entry_data = {}
        entry_data['title'] = entry.find('{http://purl.org/dc/elements/1.1/}title').text
        entry_data['creator'] = entry.find('{http://purl.org/dc/elements/1.1/}creator').text
        entry_data['publication_name'] = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}publicationName').text
        entry_data['volume'] = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}volume').text
        entry_data['issue_identifier'] = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}issueIdentifier').text if entry.find('{http://prismstandard.org/namespaces/basic/2.0/}issueIdentifier') is not None else None
        entry_data['cover_date'] = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}coverDate').text if entry.find('{http://prismstandard.org/namespaces/basic/2.0/}coverDate') is not None else None
        entry_data['doi'] = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}doi').text if entry.find('{http://prismstandard.org/namespaces/basic/2.0/}doi') is not None else None
        entry_data['affiliation'] = entry.find('{http://www.w3.org/2005/Atom}affiliation/{http://purl.org/dc/elements/1.1/}affilname').text if entry.find('{http://www.w3.org/2005/Atom}affiliation/{http://purl.org/dc/elements/1.1/}affilname') is not None else None
        entries['entry'].append(entry_data)
    return entries


# Constructing Scopus API request URL 
scopusKey = "3e98ccbfff5ed19b801086b00dfc5e36"
searchTerms = "climate change global warming"

scopusReq = f"https://api.elsevier.com/content/search/scopus?query=all({searchTerms})&sort=coverDate&count=25&apiKey={scopusKey}&view=standard&xml-decode=true&httpAccept=application%2Fxml"

# Fetching data from Scopus API
xml_data = fetch_scopus_data(scopusReq)

# if xml_data:
#     # Parsing XML and printing extracted data
#     entries = parse_xml(xml_data)
    
#     index = 1
#     while entries['offset'] < entries['count']:
#         for idx, entry in enumerate(entries['entry'], start=index):
#             print(f"Entry {idx}:")
#             for key, value in entry.items():
#                 print(f"{key}: {value}")
#             print("\n")
#         index += 25
# else:
#     print("Failed to fetch data from Scopus API.")



