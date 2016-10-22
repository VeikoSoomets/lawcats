# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2
import re
from datetime import datetime
import datetime
import logging
import urllib

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

from utils import *
#import html5lib # have to use this because politsei web has shitty/broken code, bs4 can't handle this shit alone. NB! needs to be installed in libs folder just like bs4

def clear_string(string): # to get clear dates
  string = re.sub('<br/>', '', string.rstrip())
  string = re.sub('\n', '', string.rstrip())
  string = re.sub('\r', '', string.rstrip())
  string = re.sub('\t', '', string.rstrip())
  string = re.sub(' ', '', string.rstrip())
  return string

    
def search_politsei(querywords,category,date_algus):
    results=[]
    url="https://www.politsei.ee/et/uudised/"
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(url)
    #html_contents = response.read()
    #print html_contents
    #return
    #src=urllib2.urlopen(url)
    results.extend(parse_results_politsei(response,querywords,category, date_algus))
    return results
    

def parse_results_politsei(src,querywords=None,category=None, date_algus=None):
    date_algus=datetime_object(date_algus)
    url_base="https://www.politsei.ee"
    
    #soup = bs4.BeautifulSoup(src.read())
    soup = bs4.BeautifulSoup(src.read(), 'html5lib') 
  
    results=[]
    soup = soup.findAll('dl', attrs={"class": "dotCMS-newsListing"})
    sublinks=[]
    for result in soup:
      for link in result.findAll('a', href=True):
        title=link.find_next(text=True)
        link=url_base+link.get('href')
      for item in result.findAll('dt'):  # leiame kuupäeva
        stringdate=item.find_next(text=True) #.decode('utf-8') # unicode type, muidu re ei tööta
        stringdate=clear_string(stringdate)
        stringdate=sql_normalize_date(stringdate)

        #print title, url_base+link.get('href')
      sublinks.append({'link':link,'title':title,'date':stringdate})
    
    for link in sublinks:
      if datetime_object(link['date'])>=date_algus: #datetime.datetime.now().date():
        print datetime_object(link['date'])
        print date_algus
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(link['link'])
        #html_contents = response.read()
        
        #src2=urllib2.urlopen(link['link'])
        subsoup = bs4.BeautifulSoup(response.read(), 'html5lib')

        cats=[]
        subresult = subsoup.findAll('table', attrs={'class':'newsItemContentTable'})
        for sub in subresult:
          for query in querywords:
            if query.lower() in unicode(sub).lower():
              cats.append(link['link'])
              cats.append(link['title'])
              cats.append(link['date'])
              cats.append(query)
              cats.append(category)
              if datetime_object(link['date'])>=date_algus: # checkime kuupäeva
                results.append(cats)

    return results
    #return results #  link, title, date, qword, category
 
# TESTING #####
if __name__ == "__main__":
  results=search_politsei([u'pealtnägija'],'Politsei Uudised','2015-05-01') 
  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close...')
# ########################

