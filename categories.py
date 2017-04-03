# -*- coding: utf-8 -*-
#!/usr/bin/env python
import models
from google.appengine.ext import ndb
from base_handler import BaseHandler


""" TODO: 
1) separate 'instructions/guidelines' and 'streams' ... does the user need to search for all new listings or just selected
  * only a select few sources can have an option to search for all
"""
class GenerateCategories(BaseHandler):
  """ Generates categories, subcategories and maincategories """

  @BaseHandler.logged_in2
  def get(self):
    main_categories = [
    'Eesti',
    'Arhiivid',
    'Sanktsioonid',
    'Kohturegistrid'
    ]
    dbps_main=[]
    count_main=0
    for cat in main_categories:
      count_main+=1
      dbp = models.MainCategories(maincategory_name=cat, id=cat)
      dbps_main.append(dbp)
    ndb.put_multi(dbps_main)

    dbps_sub=[]
    sub_categories = [
    {'maincategory_name':'Eesti',
    'subcategories': [
          'Eesti kohtulahendid',
          'Ministeeriumid',
          u'Õigusaktid ja eelnõud',
          u'Euroopa õigus',
          'Uudised ja foorumid'
           ]
    }
    ]
    count_sub=0
    for a in sub_categories:
      maincat_name=a['maincategory_name']
      #language=a['language']
      #print language
      for subcat in a['subcategories']:
        #for key1, value1 in value.iteritems():
        #count+=1
        count_sub+=1
        #print maincat_name, language, subcat#, key1, value1
        #dbp = models.Category(category_name=key1, category_link=value1,  subcategory_name=subcat_name)
        dbp = models.SubCategories(subcategory_name=subcat, id=subcat, parent=ndb.Key('MainCategories', maincat_name))
        dbps_sub.append(dbp)

    ndb.put_multi(dbps_sub)

    child_categories = [
    {'subcategory_name': 'Uudised ja foorumid',
      'categories': [
        ['ERR','http://www.err.ee','eesti'],
        ['Delfi','http://www.delfi.ee','eesti'],
        ['Postimees','http://www.postimees.ee','eesti'],
        [u'Õhtuleht','http://www.ohtuleht.ee','eesti'],
        [u'Päevaleht','http://epl.delfi.ee/','eesti'],
        ['Eesti Ekspress','http://ekspress.delfi.ee/','eesti'],
        ['Maaleht','http://maaleht.delfi.ee/','eesti'],
        [u'Äripäev','http://www.aripaev.ee','eesti'],
        ['raamatupidaja.ee','http://www.raamatupidaja.ee/','eesti'],
        ['juura.ee','http://juura.ee','eesti'],
        ['Riigiteataja seadusuudised', 'https://www.riigiteataja.ee/oigusuudised/seadusteUudisteNimekiri.html', 'eesti'],
        [u'Riigiteataja õigusuudised', 'https://www.riigiteataja.ee/oigusuudised/muuOigusuudisteNimekiri.html', 'eesti'],
        ['Riigikohtu uudised', 'http://www.nc.ee', 'eesti'],
    ]},
    {'subcategory_name': u'Õigusaktid ja eelnõud',
     'categories': [
         [u'Kooskõlastamiseks esitatud eelnõud', 'http://eelnoud.valitsus.ee/main#SKixD73F', 'eesti'],
         [u'Valitsusele esitatud eelnõud', 'http://eelnoud.valitsus.ee/main#SKixD73F', 'eesti'],
         [u'Riigiteataja ilmumas/ilmunud seadused', 'https://www.riigiteataja.ee/', 'eesti'],
         [u'Õigusaktide otsing', 'https://www.riigiteataja.ee/', 'eesti'],
         ['Riigiteataja seadused', 'https://www.riigiteataja.ee/', 'eesti'],
    ]},
    {'subcategory_name': u'Euroopa õigus',
     'categories': [
         ['Eur-Lex kohtuasjade rss', 'http://eur-lex.europa.eu', 'eesti'],
         ['Eur-Lex Komisjoni ettepanekute rss', 'http://eur-lex.europa.eu', 'eesti'],
         [u'Eur-Lex Parlamendi ja Nõukogu rss', 'http://eur-lex.europa.eu', 'eesti'],
         ['Eur-Lex eestikeelsete dokumentide otsing', 'http://eur-lex.europa.eu/advanced-search-form.html', 'eesti'],
     ]},
    {'subcategory_name': 'Ministeeriumid',
      'categories': [
      ['Kaitseministeerium','http://www.kaitseministeerium.ee','eesti'],
      ['Finantsministeerium','http://www.fin.ee','eesti'],
      ['Justiitsministeerium','http://www.just.ee','eesti'],
      ['Keskkonnaministeerium','http://www.envir.ee','eesti'],
      ['Kultuuriministeerium','http://www.kul.ee','eesti'],
      [u'Põllumajandusministeerium','http://www.agri.ee','eesti'],
      ['Siseministeerium','https://www.siseministeerium.ee','eesti'],
      ['Sotsiaalministeerium','http://www.sm.ee','eesti'],
      [u'Välisministeerium','http://vm.ee','eesti'],
      ['Riigikogu pressiteated', 'http://www.riigikogu.ee/index.php?id=31549', 'eesti'],
      #['Haridusministeerium','https://www.hm.ee','eesti'] # SSL block
      #['Majandusministeerium','https://www.mkm.ee','eesti'] # SSL block
    ]},
    {'subcategory_name': 'Eesti kohtulahendid',
      'categories': [
      ['Riigiteataja kohtuuudised','https://www.riigiteataja.ee/oigusuudised/kohtuuudiste_nimekiri.html','eesti'],
      ['Hiljutised Riigikohtu lahendid','http://www.nc.ee','eesti'],
      ['Riigikohtu lahendite arhiiv','http://www.nc.ee','eesti'],
      ['Maa- ja ringkonnakohtu lahendid','https://www.riigiteataja.ee/kohtuteave/maa_ringkonna_kohtulahendid/otsi.html','eesti',0],
    ]},
    ]

    count=0
    dbps=[]
    for a in child_categories:
      subcat_name=a['subcategory_name']
      categories=a['categories']
      for cat in categories:
        count+=1
        cat_name=cat[0]
        cat_link=cat[1]
        cat_lang=cat[2]
        dbp = models.Category(name=cat_name, link=cat_link, lang=cat_lang)
        dbps.append(dbp)

    """count=0
    for a in child_categories:
      subcat_name=a['subcategory_name']
      for key, value in a.iteritems():
        if type(value) is dict:
          for key1, value1 in value.iteritems():
            count+=1
            #print subcat_name, key1, value1

            dbp = models.Category(category_name=key1, category_link=value1,  subcategory_name=subcat_name)
            dbps.append(dbp) """

    ndb.put_multi(dbps)

    message="Operation successful, added %s categories, %s subcategories and %s maincategories!" % ( str(count), str(count_sub), str(count_main))
    self.render_template('sys.html',{'message_type':'success','message':message})
