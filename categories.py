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
    'Meedia',
    'Eesti',
    'USA',
    'Euroopa',
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
    {'maincategory_name':'Meedia',
    'subcategories': [
          'Eesti Meedia',
          u'US & UK Meedia',
          u'Saksa Meedia',
          u'Soome Meedia',
          u'Vene Meedia'
           ]
    },
    {'maincategory_name':'Eesti',
    'subcategories': [
          'Kohtud ja kohtulahendid',
          'Ministeeriumid',
          u'Advokaadi- ja õigusbürood',
          u'Õigusaktid',
          'Ametid ja inspektsioonid',
          'Muu'
           ]
    },
    {'maincategory_name': 'USA',
    'subcategories': [
          'OFAC, FATF, FinCEN'
          ]
    },
    {'maincategory_name': 'Euroopa',
    'subcategories': [
          'Eur-LEX',
          ]
    },
    {'maincategory_name': 'Arhiivid',
    'subcategories': [
          'Eesti meediaarhiivid',
          'Vene meediaarhiivid',
          'Ametite ja inspektsioonide arhiivid',
          u'Õigusaktide arhiivid'
          ]
    }, 
    {'maincategory_name': 'Sanktsioonid',
    'subcategories': [
          u'EU & USA',
          ]
    },
    {'maincategory_name': 'Kohturegistrid',
    'subcategories': [
          'Eesti Kohtud',
          'Euroopa Kohtud'
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
    {'subcategory_name': 'Muu', 
      'categories': [
        ['Riigihanked','https://riigihanked.riik.ee','eesti'],
        ['Riigikogu pressiteated','http://www.riigikogu.ee/index.php?id=31549','eesti'],
    ]},
    {'subcategory_name': 'Eesti Meedia',
      'categories': [
        ['ERR','http,//www.err.ee','eesti'],
        ['Delfi','http,//www.delfi.ee','eesti'],
        ['Postimees','http,//www.postimees.ee','eesti'],
        [u'Õhtuleht','http,//www.ohtuleht.ee','eesti'],
        [u'Päevaleht','http,//epl.delfi.ee/','eesti'],
        ['Eesti Ekspress','http,//ekspress.delfi.ee/','eesti'],
        ['Maaleht','http,//maaleht.delfi.ee/','eesti'],
        [u'Äripäev','http,//www.aripaev.ee','eesti'],
        [u'Õigus & Kord uudised' , 'http,//oiguskord.ee','eesti'],
        [u'Õigus & Kord foorum','http,//oiguskord.ee/Foorum','eesti'],
        ['raamatupidaja.ee','http,//www.raamatupidaja.ee/','eesti'],
        ['juura.ee','http,//juura.ee','eesti'],
    ]},
    {'subcategory_name': 'US & UK Meedia',
      'categories': [
        ['Reuters','http,//feeds.reuters.com','english'],
        ['BBC','http,//www.bbc.com','english'],
        ['CNN','http,//edition.cnn.com/','english'],
        ['Forbes','http,//www.forbes.com','english'],
        ['TIME','http,//time.com/','english'],
        ['New York Post','http,//nypost.com/','english'],
        ['Wall Street Journal','http,//online.wsj.com','english'],
        ['Marketwatch','http,//www.marketwatch.com','english'],
        ['The Economist','http,//www.economist.com/','english'],
        ['Financial Times','http,//www.ft.com','english'],
        ['Business Insider','http,//www.businessinsider.com','english'],
        ['Bloomberg','http,//www.bloomberg.com','english'],
        ['The Guardian','http,//www.theguardian.com','english'],
        ['MarketWatch','http,//www.marketwatch.com','english'],
    ]},
    {'subcategory_name': 'Soome Meedia',
      'categories': [
        ['Helsingin Sanomat','http://www.helsinkitimes.fi/','english'],
    ]},
    {'subcategory_name': 'Saksa Meedia', 
      'categories': [
        ['Deutche Welle','http://www.dw.de/','english'],
    ]},
    {'subcategory_name': 'Vene Meedia', 
      'categories': [
        [u'Деловное Деломости','http://www.dv.ee/',u'русский'], # venekeelne äripäev
        [u'МК-Эстония','http://www.mke.ee/',u'русский'],
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
      #['Haridusministeerium','https://www.hm.ee','eesti'] # SSL block
      #['Majandusministeerium','https://www.mkm.ee','eesti'] # SSL block
    ]},
    {'subcategory_name': u'Advokaadi- ja õigusbürood', 
      'categories': [
      ['Eversheds Ots & Co','http://www.eversheds.com','eesti'],
      ['Lawin','http://www.lawin.ee','eesti'],
      ['Redbaltic','http://www.redbaltic.com','eesti'],
      ['Sorainen','http://www.sorainen.com','eesti'],
      ['Varul','http://www.varul.com','eesti'],
      ['Aivar Pilv','http://apilv.ee','eesti'],
      ['Alterna','http://alternalaw.ee','eesti'],
      ['Borenius','http://borenius.ee','eesti'],
      ['Concordia','http://www.concordia.ee','eesti'],
      ['Baltic Legal Solutions','http://www.blslawfirm.com','eesti'],
      ['Glimstedt','http://www.glimstedt.ee','eesti'],
      ['Tark Grunte Sutkiene','http://www.tarkgruntesutkiene.com','eesti'],
      ['Varul Publikatsioonid','http://www.varul.com/publikatsioonid/','eesti'],
      [u'Raidla, Lejins & Norcou','http://www.rln.ee','eesti'],
    ]},
    {'subcategory_name': 'Eur-LEX', 
      'categories': [
      ['eurlex kohtuasjad','http://eur-lex.europa.eu','eesti'],
      ['eurlex komisjoni ettepanekud','http://eur-lex.europa.eu','eesti'],
      [u'eurlex parlament ja nõukogu','http://eur-lex.europa.eu','eesti'],
    ]},
    {'subcategory_name': u'Õigusaktid', 
      'categories': [
      ['Riigiteataja seadusuudised','https://www.riigiteataja.ee/oigusuudised/seadusteUudisteNimekiri.html','eesti'],
      [u'Riigiteataja õigusuudised','https://www.riigiteataja.ee/oigusuudised/muuOigusuudisteNimekiri.html','eesti'],
      [u'Kooskõlastamiseks esitatud eelnõud','http://eelnoud.valitsus.ee/main#SKixD73F','eesti'],
      [u'Valitsusele esitatud eelnõud','http://eelnoud.valitsus.ee/main#SKixD73F','eesti'],
      [u'Riigiteataja ilmumas/ilmunud seadused','https://www.riigiteataja.ee/','eesti'],
      ['Riigiteataja seadused','https://www.riigiteataja.ee/','eesti'],
    ]},
    {'subcategory_name': 'Kohtud ja kohtulahendid', 
      'categories': [
      ['Riigiteataja kohtuuudised','https://www.riigiteataja.ee/oigusuudised/kohtuuudiste_nimekiri.html','eesti'],
      ['Riigikohtu uudised','http://www.nc.ee','eesti'],
      ['Riigikohtu lahendid','http://www.nc.ee','eesti'],
      ['Maa- ja ringkonnakohtu lahendid','https://www.riigiteataja.ee/kohtuteave/maa_ringkonna_kohtulahendid/otsi.html','eesti'],
    ]},
    # ######### Kohturegistrid
    {'subcategory_name': 'Eesti Kohtud', 
      'categories': [
      ['Riigikohtu lahendite arhiiv','http://www.nc.ee','eesti'],
      ['Maa- ja ringkonnakohtu lahendid ','https://www.riigiteataja.ee/kohtuteave/maa_ringkonna_kohtulahendid/otsi.html','eesti'], # to avoid duplicates, add space here
    ]},
    {'subcategory_name': 'Euroopa Kohtud', 
      'categories': [
      ['Euroopa Inimõiguste Kohus','#','eesti'],
    ]},
    # ######### Arhiivid
    {'subcategory_name': 'Eesti meediaarhiivid', 
      'categories': [
      ['Delfi arhiiv','http://www.delfi.ee/archive','eesti'],
      [u'Äripäev arhiiv','http://www.aripaev.ee/mod/otsing/arhiiv','eesti'],
      [u'raamatupidaja.ee otsing','http://www.raamatupidaja.ee/search','eesti'],
      [u'Õhtuleht arhiiv','http://www.postimees.ee/search','eesti']
    ]},
    {'subcategory_name': 'Vene meediaarhiivid', 
      'categories': [
      [u'Деловное Деломости архив','http://www.dv.ee',u'русский'],
      [u'МК-Эстония поиск','http://www.mke.ee',u'русский'],
    ]},
    {'subcategory_name': 'Ametite ja inspektsioonide arhiivid', 
      'categories': [
      ['Politsei uudiste arhiiv','http://www.politsei.ee','eesti'],
    ]},
    {'subcategory_name': u'Õigusaktide arhiivid',
      'categories': [
      [u'Eelnõude otsing','https://www.riigiteataja.ee/eelnoud/otsing.html','eesti'],
      [u'Kehtivate õigusaktide otsing','https://www.riigiteataja.ee/tervikteksti_otsing.html','eesti'],
      [u'Kehtivate KOV õigusaktide otsing','https://www.riigiteataja.ee/tervikteksti_otsing.html?kov=true','eesti'],
    ]},
    # ######### Sanctions
    {'subcategory_name': 'EU & USA', 
      'categories': [
      ['OFAC Sanctions','#','english'],
      ['EU Sanctions','#','english'],
    ]},
    # ######### Monitoring
    {'subcategory_name': 'Ametid ja inspektsioonid', 
      'categories': [
      [u'euroopa pangandusjärelevalve EBA','http://www.fi.ee/index.php?id=13371&year=2014','eesti'],
      ['EIOPA teated','http://www.fi.ee/index.php?id=13373&year=2015','eesti'],
      ['ESMA teated','http://www.fi.ee/index.php?id=13375&year=2015','eesti'],
      ['FI pressiteated','http://www.fi.ee/index.php?id=1080&year=2015','eesti'],
      ['FI juhendite projektid',"http://www.fi.ee/index.php?id=2898",'eesti'],
      ['FI kehtivad juhendid',"http://www.fi.ee/index.php?id=2897",'eesti'],
      [u'ühtne pangandusjärelevalve SSM' ,'http://www.fi.ee/index.php?id=16881&year=2014','eesti'],
      ['Politsei uudised','https://www.politsei.ee/et/uudised/','eesti'],
      ['Ametlikud teadaanded', 'https://www.ametlikudteadaanded.ee/','eesti'],
    ]},
    {'subcategory_name': 'OFAC, FATF, FinCEN',
      'categories': [
      ['OFAC Recent Actions', 'http://www.treasury.gov/resource-center/sanctions/OFAC-Enforcement/Pages/OFAC-Recent-Actions.aspx','english'], 
      ['FATF', 'http://www.fatf-gafi.org/','english'], 
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
        dbp = models.Category(category_name=cat_name, category_link=cat_link,  subcategory_name=subcat_name, language=cat_lang)
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
    self.render_template('admin.html',{'message_type':'success','message':message})
    
  