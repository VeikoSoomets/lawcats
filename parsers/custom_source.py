# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
from bs4 import SoupStrainer
import urllib2
import html5lib
import logging
import re

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

#from parsers import rss_parse as rp
#import models


def find_rss(link):
  if not link.startswith('http', 0, 4):
      link = 'http://' + link

  """ We need these headers because sometimes we are forbidden """
  hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
     'Accept-Encoding': 'none',
     'Accept-Language': 'en-US,en;q=0.8',
     'Connection': 'keep-alive'}
  req = urllib2.Request(link, headers=hdr)  # , headers=hdr
  src = urllib2.urlopen(req)
  encoding = src.headers['content-type'].split('charset=')[-1]  # we have to use this fix or EE letters are causing trouble
  soup = bs4.BeautifulSoup(src.read(), "html5lib", from_encoding=encoding)
  title = soup.title.string
  rss_link = False

  # finds only the first - if we want to find all RSS, then findAll, and make sure to take title from each individual RSS source
  # (else it will be same for all, which might cause problems)
  try:
    soup2 = soup.find('link', attrs={"type": "application/rss+xml"})
    if not soup2:
      soup2 = soup.find('a', {"class": "rss"})
    rss_link = soup2.get('href')

    # test what happens with httpounds.com? also, make sure https will work when changing logic
    if not rss_link.startswith('http', 0, 4):
      rss_link = link + rss_link

    found_result = {'link': rss_link, 'title': title}

  except Exception, e:
    soup2 = soup.findAll('a')
    for link in soup2:
      if 'rss.' in link.get('href'):
        rss_link = link.get('href')

    if rss_link:
      found_result = {'link': rss_link, 'title': title}
    else:
      found_result = False

  return found_result

only_p_tags = SoupStrainer("p")


def blogs_handler(link,querywords=None,category=None):
  """ We need these headers because sometimes we are forbidden """
  hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
     'Accept-Encoding': 'none',
     'Accept-Language': 'en-US,en;q=0.8',
     'Connection': 'keep-alive'}
  req = urllib2.Request(link, headers=hdr)  # , headers=hdr
  src = urllib2.urlopen(req)
  encoding = src.headers['content-type'].split('charset=')[-1]  # we have to use this fix or EE letters are causing trouble
  soup = bs4.BeautifulSoup(src.read(), "html5lib", from_encoding=encoding)

  blog_title = soup.title.string
  results = []
  """ Get articles by different methods - try, which has more results (blogs usually show more than 2 posts per page) """
  articles = []
  article_divs = ['article', 'doc-article', 'article_preview', 'post', 'entry', 'ArticleExcerpt']
  for value in article_divs:
    try:
      potential_articles = soup.find_all('div', attrs={'class': value})  # or by div
      if len(potential_articles) >= 2:
        articles = potential_articles
        break
      potential_articles = soup.find_all(value)
      if len(potential_articles) >= 2:
        articles = potential_articles
        break
    except Exception:
      pass

  if not articles:
    return False, None

  final_results = []
  for article in articles:
    resultset = []
    article_link, title, content = None, None, None
    try:
      # Get title and link
      title_tags = ['h2', 'h1', 'h3', 'h4', 'h5']
      for tag in title_tags:
        try:
          title = article.find(tag).find('a')
          article_link = title.get('href')
          title = title.stripped_strings.next()
          if not article_link.startswith('http:', 0, 5):
            article_link = link + article_link
        except Exception, e:
          pass
        if title:
          break

      if not title:
        title = article.find('a')
        article_link = title.get('href')
        title = title.stripped_strings.next()

      resultset.append(article_link)
      resultset.append(title)

      # Get content
      content_divs = ['post-content','content','article-content','post-container','postcontainer','post-content','post_content','article_content']
      content = article.find_all(only_p_tags)[:]
      if not content:
        for value in content_divs:
          try:
            content = soup.findAll('div', attrs={'class': value})
            content = [x.stripped_strings.next() for x in content]
          except Exception, e:
            print "got this error"
            print e
            pass
          if content:
            break
      resultset.append(content)
      final_results.append(resultset)
    except Exception, e:
      print e
      continue

  # If we are searching
  if querywords:
    for search_ in final_results:
      for x in querywords:
        if ' ' in x:
          new_x=set(x.split(' ')) # add to a set
        elif x=='':
          new_x=''
        else:
          new_x=[x]
        if (all([x2.lower() in search_[1].lower()+search_[2][0].get_text().lower() for x2 in new_x]) ):
          results.append([search_[0],search_[1],'date',x,category])
  else:
    if len(resultset)>0:
      results = True

  return results, blog_title

# TESTING #####
if __name__ == "__main__":
  link1 = 'http://blogs.wsj.com/law/'
  link2 = 'http://www.manrepeller.com/'
  link3 = 'http://www.nomadicmatt.com/travel-blog/'
  link4 = 'http://www.physorg.com'
  link5 = 'http://googleblog.blogspot.com.ee/' 
  link6 = 'http://www.cannalawblog.com/'
  link7 = 'http://www.theleangreenbean.com/'
  link8 = 'http://kikutrenniblogi.ee/'
  link9 = 'http://www.computeraudiophile.com/'
  link10 = 'http://www.dragonweb.eu/et/blog.html'
  link11 = 'http://annestiil.ohtuleht.ee/blogid/ilublogi'
  link12 = 'http://www.conservativehome.com/'
  link13 = "http://www.banki.ru/news/"
  link14 = "http://www.ediscoverylaw.com"
  link15 = "http://www.popehat.com"
  link16 = "http://blogs.loc.gov/law/"

  link17 = "http://www.miningweekly.com/page/diamonds"
  link18 = "http://www.mining.com/diamond/"
  link19 = "http://www.ndtv.com/topic/indian-diamond/news"
  link24 = "http://investingnews.com/category/daily/resource-investing/gem-investing/diamond-investing/"

  link20 = "http://timesofindia.indiatimes.com/topic/Diamond-industry"  # doesnt work
  link21 = "http://www.idexonline.com/index.aspx" # doesnt work
  link22 = "https://www.awdc.be/en/news" # doesnt work
  link23 = "http://en.israelidiamond.co.il/english/diamond-news" # doesnt work, search for <a>RSS</a>
  link25 = "http://www.diamonds.net/News/Articles.aspx" # doesnt work, search for <a><img src="%rss%" /></a>

  link26 = "www.bbc.com/news"


  # http://stackoverflow.com/questions/13303449/urllib2-httperror-http-error-403-forbidden

  #results, blog_title = blogs_handler(link25, querywords=[''])
  results = find_rss(link26)
  # print blog_title
  if results is False:
    print "Didn't manage to read structure"
  else:
    for result in results:
      print result, '\n'

  #raw_input('press enter to close..')
  # TODO! Check if searching for results and adding to database, add only new ones (seems to be duplicates for some sources)
# ########################
