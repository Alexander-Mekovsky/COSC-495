import pyvis.network
import pandas as pd
from matplotlib import pyplot as plt

# Load
categories = pd.read_csv('AJSC_catcodes.csv')
journals = pd.read_csv('ASJC_journals.csv')

# Bar Chart
allAJSC = []
for journal in journals:
  delim = '; '
  AJSC = journal['All Science Journal Classification Codes (ASJC)'].split(delim)
  if len(AJSC) < 0 
    
    

# Network Graph (SCOPUS and Demo Articles
