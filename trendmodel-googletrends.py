from nltk import word_tokenize
from gensim.models import KeyedVectors
import time
from pytrends.request import TrendReq
pytrends = TrendReq()
import pandas as pd
pd.options.display.max_colwidth = 150
from colorama import Fore, Back, Style
from nltk.corpus import stopwords
from googlesearch import search

start=time.time()
print("\n")

def all_lower(my_list):
    return [x.lower() for x in my_list]

def isDigit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    

# Creating a database for similar words
sample1 = open("SampleTextTM1.txt", "r").read()
sample1=sample1.lower()
s1=word_tokenize(sample1)
sample1a = open("SampleTextTM2.txt", "r").read()
sample1a=sample1a.lower()
s1a=word_tokenize(sample1a)

filename = 'GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

blres=[]
for el in s1:
    result = model.most_similar(positive=[el], topn=5)
    if isDigit(el)==False:
        blres.append(el)
        blres.append(result)
    
blres=str(blres).lower()
blres=word_tokenize(blres)

#Removing stopwords from sample1
stop_words = stopwords.words('english')
sample2 = open("StopWords_Custom.txt", "r").read().lower()
s2=word_tokenize(sample2)
stop_words_new = stop_words.extend(s2)

appendFile1 = open('filteredtext.txt','w').close()
for r in blres:

    if not r in stop_words:
        
        appendFile = open('filteredtext.txt','a')
        appendFile.write(" "+r)
        appendFile.close()             

sample3 = open("filteredtext.txt", "r").read().lower()
s3=word_tokenize(sample3)

blres2=[]
for i in range(0,len(s3)):
    a=s3[i].replace("'","")
    a=a.replace("_"," ")
    if isDigit(a)==False:
        blres2.append(a)
blres2=list(set(blres2+s1a))
print(blres2)

#Getting PyTrends search results
sample4 = open("Trending_words.txt", "r").read().lower()
l=word_tokenize(sample4) 
#l=['diabetes']
#del l[:(len(l)-5)]
blank=[]
b_al1=pd.DataFrame()
b_bl1=pd.DataFrame()

for el in l:
    kw_list =[el] 
    pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
    rq=pytrends.related_queries()
    
    st=str(rq).split("  ") 
    a = list(filter(lambda x: x != '', st)) #Removing blank elements

    res1 = [a[i] for i in range(len(a)) if i % 2 != 0] #Splitting a into two groups

    al=[] #blank list
    for el in res1:
        al.append(el)


    res2 = [a[i] for i in range(1,len(a)) if i % 2 == 0]

    bl=[] #blank list
    for el in res2:
        b=el.split()
        if len(b)!=2:
            continue
        del b[1]
        bl.append(' '.join(map(str, b)))

    bl=list(map(lambda x: x.replace(",",""),bl)) #Removing commas

    df = pd.DataFrame(list(zip(al, bl)), columns =['Name', 'Values'])

    tf = df[df['Name'].str.contains('query')]
    litf=list(tf.index)
    del litf[0]
    ledf=len(df.index)
    al1=df.loc[0:(litf[0]-1),:]
    b_al1=b_al1._append(al1) #Top results dataframe
    bl1=df.loc[litf[0]:ledf,:]
    b_bl1=b_bl1._append(bl1) #Rising results dataframe

    blank=blank+al
    time.sleep(1)

#Blank is the list with all search titles
#blres2 is the list with all custom words (stopwords removed)

#Checking for same words
sam = str()
for wd in blres2:
  for wd2 in blank: 
      if wd2.find(wd)>=0:
         sam=sam+(' ')+wd

sam=word_tokenize(sam)
sam=set(sam) #Unique keywords
l2=all_lower(blank)
l_al=all_lower(b_al1)
l_bl=all_lower(b_bl1)
dfa=pd.DataFrame()
dfb=pd.DataFrame()

#Displaying the titles
for el in sam:
    dfa=dfa._append(b_al1[b_al1['Name'].str.contains(el)])

for el in sam:
    dfb=dfb._append(b_bl1[b_bl1['Name'].str.contains(el)])

#Getting the products for Top

querylist=list(dfa['Name'])
x=0
blist=[] #Product Link
blist2=[] #Topic

for k in range(0,len(querylist)):
    sch= querylist[k]  #Search result
    query = ('kapiva '+sch)
    for j in search(query, tld="co.in", num=10, stop=6, pause=2):
        if j != ('https://kapiva.in/') and j != ('https://kapiva.in/kapiva/') and j.find('kapiva')>=0 and j.find('blog')<=0 and j.find('https://kapiva.in/')>=0:           
            blist.append(j)
            blist2.append(sch)
            x=x+1
            if len(j[x])>0:
                break
    for el in search(query, tld="co.in", num=10, stop=1, pause=2):
        blist.append("\n"+el)
        
df2 = pd.DataFrame(list(zip(blist2, blist)),
               columns =['Topic', 'Product'])

res = (pd.merge(dfa, df2, left_on='Name', right_on='Topic', how='left').drop('Name', axis=1))
print(Fore.GREEN+"The TOP search results are :"+Fore.WHITE+"\n")
fres=(res.dropna().drop_duplicates())
print(fres)
print("\n")

#Getting the products for RISING

querylist=list(dfb['Name'])
x=0
blist=[]
blist2=[]
for k in range(0,len(querylist)):
    sch= querylist[k]  #Search result
    query = ('kapiva '+sch)
    for j in search(query, tld="co.in", num=10, stop=6, pause=2):
        if j != ('https://kapiva.in/') and j != ('https://kapiva.in/kapiva/') and j.find('kapiva')>=0 and j.find('blog')<=0 and j.find('https://kapiva.in/')>=0:           
            blist.append(j)
            blist2.append(sch)
            x=x+1
            if len(j[x])>0:
                break
            
    for el in search(query, tld="co.in", num=10, stop=1, pause=2):
        blist.append("\n"+el)

df3 = pd.DataFrame(list(zip(blist2, blist)),
               columns =['Topic', 'Product'])

res2 = (pd.merge(dfb, df3, left_on='Name', right_on='Topic', how='left').drop('Name', axis=1))
print(Fore.GREEN+"The RISING search results are :"+Fore.WHITE+"\n")
fres2=(res2.dropna().drop_duplicates())
print(fres2)
print("\n")

dfres=df2+df3
print(dfres)

#Saving result in a sheet
dfres.to_csv("Trendresult.csv")

end=time.time()
time=str(end-start)
print("\n"+Fore.GREEN+"Time elapsed: "+Fore.WHITE+time+" seconds")
