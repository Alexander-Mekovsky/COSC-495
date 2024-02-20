import pyvis.network
import pandas as pd
from matplotlib import pyplot as plt

# Load
catFile = pd.read_csv('AJSC_catcodes.csv')
journalFile = pd.read_csv('ASJC_journals.csv')

catDict = []
for category in catFile:
  catDict

# Bar Chart
catCount = {}
for codes in journalFile['All Science Journal Classification Codes (ASJC)']:
  delim = '; '
  AJSC = codes.split(delim)
  catCount[len(AJSC)] += 1

plt.bar(catCount.keys(), catCount.values())

  
    
    

# Network Graph (SCOPUS and Demo Articles
