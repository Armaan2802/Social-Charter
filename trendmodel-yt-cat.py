from tqdm import tqdm
import requests
import json
from jsonpath_ng import jsonpath, parse
import pandas as pd
pd.options.display.max_colwidth = 150
from nltk import word_tokenize
import time
from colorama import Fore 

YOUR_API_KEY=""
url = "https://www.googleapis.com/youtube/v3/videos?key="+[YOUR_API_KEY]

pages = ['CDIQAQ', 'CDIQAA', 'CGQQAA', 'CJYBEAA']

cat=[0,19,22,26]

al=[]
bl=[]
cl=[]

for k in range(0,len(cat)):
    for i in range(0, len(pages)):
        params = {
            "chart": "mostPopular",
            "regionCode": "IN",
            "part": "statistics, snippet",
            "videoCategoryId": cat[k],
            "maxResults": "50",
            "pageToken": pages[i]
        }

        r = requests.get(url=url, params=params)
        if i == 0 and k == 0:
            print("Status initial:", r.status_code)
        
        res = r.text
        res = json.loads(res)

        expression1 = parse('$.items[*].snippet.title')
        expression2 = parse('$.items[*].statistics.viewCount')
        expression3 = parse('$.items[*].snippet.tags')

        for match in expression1.find(res):
            al.append((match.value).lower())

        for match in expression2.find(res):
            bl.append(int(match.value))

        for match in expression3.find(res):
            cl.append(match.value)

        ref = 50*(i+1)

        if ref > len(al):
            break


df1 = pd.DataFrame(list(zip(al, bl)),
                   columns=['Title', 'Views'])

print(len(al))
print("Initial Table:\n", df1)

#Time Delay

it = 3600 #Sleep time in seconds
print("\nTime Delay: "+ str(it/60) +" mins")
for i in tqdm(range(it), desc="Sleeping"):
    time.sleep(1)

#Table 2 begins

al2=[]
bl2=[]

for k in range(0,len(cat)):
    for i in range(0, len(pages)):
        params = {
            "chart": "mostPopular",
            "regionCode": "IN",
            "part": "statistics, snippet",
            "videoCategoryId": cat[k],
            "maxResults": "50",
            "pageToken": pages[i]
        }

        r2 = requests.get(url=url, params=params)

        if i==0 and k==0:
            print("\nStatus final:", r2.status_code)
    
        res2 = r2.text
        res2 = json.loads(res2)

        for match in expression1.find(res2):
            al2.append((match.value).lower())

        for match in expression2.find(res2):
            bl2.append(int(match.value))

        ref = 50*(i+1)

        if ref > len(al2):
            break


df2 = pd.DataFrame(list(zip(al2, bl2)),
                   columns=['Title', 'Views'])

print(len(al2))
print("Final Table:\n", df2)

#df1 is initial table and df2 is final table
print("\n\n\n")

newdf = pd.merge(df1, df2, how='inner', on="Title", suffixes=('_initial', '_final'))

v1 = list(newdf['Views_initial'])
v2 = list(newdf['Views_final'])

l=len(v1) 
perc=[]
for i in range(0,l):
    sub=((float(v2[i])-float(v1[i]))/float(v1[i]))
    per=float(sub)*100*1000
    perc.append(per)

newdf['ViewChange(% *1000)'] = perc
print(Fore.GREEN+"\n\nFinal Output:\n"+Fore.WHITE)
newdf = newdf.sort_values(by='ViewChange(% *1000)', ascending=False)

dfall = pd.DataFrame(
    columns=['Title', 'Views_initial', 'Views_final', 'ViewChange(% *1000)'])

word=['fit','australia','dandruff','diabetes']

for el in word:
    curd = el.lower().strip()
    filt = newdf[newdf['Title'].str.contains(el)]
    dfall = pd.concat([dfall, filt]).drop_duplicates()

print(Fore.GREEN+"Keywords used: "+Fore.WHITE ,word)
dfall = dfall.sort_values(by='ViewChange(% *1000)', ascending=False)
print(dfall)
print(Fore.GREEN+"\nTotal Search Results: "+Fore.WHITE, len(al2))
print(Fore.GREEN+"Total Matches: "+Fore.WHITE, len(dfall['Title']))
print("\n")

