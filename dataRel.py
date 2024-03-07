import pandas as pd
from matplotlib import pyplot as plt
from collections import defaultdict #defaults dict entry to 0
import atexit
import data_loader as dl
import display_graph as dg
import fetch_api as fa

# def goodbye():
#     print(header['offset'], entries['count'],searchTerms)
# atexit.register(goodbye)

# Initialize key maps for reading the file
topCatsKeyMap = {
    "Description": 'desc',
    "Supergroup": 'su'
}
allCatsKeyMap = {
    "Description": 'desc'
}
journalsKeyMap = {
    "Publisher's Name": 'pub',
    "Publisher imprints grouped to main Publisher": 'gpub',
    "Source Title": 'stit',
    "Print-ISSN": 'pissn',
    "E-ISSN": 'eissn',
    "Active or Inactive": 'act',
    "Coverage": 'cvg',
    "Article language in source (three-letter ISO language codes)": 'lang',
    "Medline-sourced Title? (See additional details under separate tab.)": 'mdl',
    "Articles in Press included?": 'aip',
    "Source Type": 'styp',
    "Related title 1": 'r1',
    "Other related title 2": 'r2',
    "Other related title 3": 'r3',
    "Other related title 4": 'r4',
    "All Science Journal Classification Codes (ASJC)": 'asjc'
}
acatFile = pd.read_csv('catNames.csv', encoding ='latin-1')
tcatFile = pd.read_csv('topCats.csv', encoding='latin-1')
journalFile = pd.read_csv('journals.csv', encoding ='latin-1')

dl.loadcsv(acatFile,allCatsKeyMap,'Code')
dl.loadcsv(tcatFile,topCatsKeyMap, 'code')
dl.loadcsv(journalFile, journalsKeyMap, 'Sourcerecord ID')

# Initialize your dictionaries
superCats = defaultdict(int)
topCats = {}
allCats = {}

for group in tcatFile["Supergroup"]:  # Direct column name reference
    superCats[group] += 1

for _, row in tcatFile.iterrows():
    desc = row["Description"]
    topCats[str(row['code'])] = {
        'desc': desc,
        'freq': 0
    }

for _, row in acatFile.iterrows():
    desc = row["Description"]
    allCats[str(row['Code'])] = {
        'desc': desc,
        'freq': 0
    }


# Network Dictionaries for categories
key = "All Science Journal Classification Codes (ASJC)"
journalCats, catNetEdges, allCats= dl.freq_loadcsv(journalFile,allCats,key)



# Display the basic bar charts of the categories
# dg.barchart(journalCats.keys(),journalCats.values(),'Number of Categories','Number of Journals','Frequency of Journal Distribution Across Categories',tight=True)
# dg.closeplot()

# _, _, topCats = dl.freq_loadcsv(journalFile,topCats,key, suff="**",end=2, net=False)
# sorted_topCats = dict(sorted(topCats.items()))
# Extract keys and values from sorted dictionary
# keys = [item['desc'] for item in sorted_topCats.values()]
# values = [item['freq'] for item in sorted_topCats.values()]
# dg.barchart(keys,values,'CategoryID','Number of Journals','Frequency of Categories in Journals',tight=True)
# dg.closeplot()

# Prompt user to input top-level categories
# user_input = input("Enter top-level categories (separated by comma), or press Enter to include all: \n")
# selCats = user_input.split(',') if user_input else None
# print(dg.freq_network(topCats,catNetEdges,selCats,end=2,suff='**'))

scopusKey = "3e98ccbfff5ed19b801086b00dfc5e36"
searchTerms = "climate change global warming ocean atmosphere moon star"

status_message = fa.index_scopus_response(scopusKey,searchTerms)
print(status_message)