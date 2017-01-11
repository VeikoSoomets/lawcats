def get_urls():
  src=urllib2.urlopen('https://www.riigiteataja.ee/lyhendid.html',timeout=60)
  urllist=[]
  soup = bs4.BeautifulSoup(src)
  soup = soup.find('div', attrs={"id": "content"})
  for result in soup.findAll('tr'):
      law = result.findAll('td')[0]
      linkitem = result.findNext('a', href=True).get('href')
      url = "https://www.riigiteataja.ee/%s?leiaKehtiv" % linkitem
      urllist.append(url)
      return urllist

