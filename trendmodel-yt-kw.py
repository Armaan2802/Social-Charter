import requests
import json
from jsonpath_ng import jsonpath, parse
import pandas as pd
pd.options.display.max_colwidth = 150

url = "https://www.googleapis.com/youtube/v3/search?key=AIzaSyBmgz_gkQ5b8R8XxS-k2UvkzdfkQw5k-LE"

pages = ['CDIQAQ', 'CDIQAA', 'CGQQAA', 'CJYBEAA']

params = {
    "chart": "mostPopular",
    "regionCode": "IN",
    "part": "snippet",
    "maxResults": "50",
    "q":"shampoo",
    "type":"video",
    "order": "viewCount"
}

r = requests.get(url=url, params=params)

print(r.status_code)
res = r.text
res = json.loads(res)

al = []
bl = []
cl = []

expression1 = parse('$.items[*].snippet.title')
# expression2 = parse('$.items[*].statistics.viewCount')
# expression3 = parse('$.items[*].snippet.tags')

for match in expression1.find(res):
    al.append(match.value)

print(len(al))

df=pd.DataFrame(al, columns=['Title'])
print(df)
