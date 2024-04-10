import pandas as pd
from matplotlib import pyplot as plt


acatFile = pd.read_csv('catNames.csv', encoding ='latin-1')
tcatFile = pd.read_csv('topCats.csv', encoding='latin-1')
journalFile = pd.read_csv('journals.csv', encoding ='latin-1')
api_data = pd.read_csv('climate-change-global-warming-ocean-atmosphere-moon-star.csv',encoding='latin-1')



asjc = 'All Science Journal Classification Codes (ASJC)'

# for index,api_row in api_data.iterrows():
#     journal_title = api_row['Publication Name'].split(',')[0]
    


#     for i, journal_row in journalFile.iterrows(): 
         
#      if journal_title == journal_row["Source Title"]: 
#              print("success")
             
#              categories = str(journal_row[asjc]).split(';')

#              all_cats = [cat for cat in categories if not cat.startswith("23") ]
api_data['journal title'] = api_data['Publication Name'].str.split(',').str[0]

merger = pd.merge(api_data,journalFile,left_on="journal title",right_on = "Source Title")
merger['Categories'] = merger[asjc].str.split(';')



all_cats = merger['Categories'].explode().dropna().tolist()
print(type(all_cats))
cat_names = []

for cats in all_cats: 

    for index,tops in tcatFile.iterrows(): 
        if cats[:2] == tops['code'][:2]: 
            cat_names.append(tops['Description'])


category_counts = pd.Series(cat_names).value_counts()

plt.bar(category_counts.index, category_counts.values)
plt.title('Category Counts')
plt.xlabel('Category')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.show()
