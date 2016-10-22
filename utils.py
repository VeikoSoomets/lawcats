# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 Kaspar Gering.
#
""" Contains 'helper' classes for managing search results.
"""
import datetime
import re

def clear_string(string): # to get clear dates
  string = re.sub('<br/>', '', string.rstrip())
  string = re.sub('\n', '', string.rstrip())
  string = re.sub('\r', '', string.rstrip())
  string = re.sub('\t', '', string.rstrip())
  string = re.sub(' ', '', string.rstrip())
  return string
  
def clear_string2(string): # to get clear dates
  string = re.sub('<br/>', '', string.rstrip())
  string = re.sub('\n', '', string.rstrip())
  string = re.sub('\r', '', string.rstrip())
  string = re.sub('\t', '', string.rstrip())
  string = re.sub('  ', '', string.rstrip())
  return string

def datetime_object(date):
    """ Make dates ready for inserting into datastore Add new formats if needed. """
    try: 
        date=datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        date=datetime.datetime.now().date()
    return date

def sql_normalize_date(date):
    """ Make dates ready for inserting into SQL. Add new formats if needed. """
    EE_dates = {
    'jaanuar' : '01',
    'jaan' : '01',
    u'январь' : '01',
    'veebruar' : '02',
    'veeb' : '02',
    'veebr' : '02',
    u'февраль' : '02',
    u'märts' : '03',
    u'март' : '03',
    'aprill' : '04',
    'aprill' : '04',
    u'апреля' : '04',
    'mai' : '05',
    u'мая' : '05',
    'juuni' : '06',
    u'июнь' : '06',
    'juuli' : '07',
    u'июль' : '07',
    'august' : '08',
    'aug' : '08',
    u'август' : '08',
    'september' : '09',
    'sept' : '09',
    u'сентябрь' : '09',
    'oktoober' : '10',
    'okt' : '10',
    u'октября' : '10',
    'november' : '11',
    'nov' : '11',
    u'ноябрь' : '11',
    'detsember' : '12',
    'dets' : '12',
    u'декабрь' : '12'
    }   
    
    """ Dates from string, EE """
    for key, month in EE_dates.iteritems():
      if key in date:
        try: # have to use this, because substring will not be found error will be thrown there are no dots in date
          if date.index('.')==1: # in case day is without preceding zero
            day='0' + date[0]
          else:
            day=date[0:2]
        except Exception:
          day=date[0:2]
        date=day + '.' + month + '.' + date[-4:]
    
    try: 
        if date.index('.')==4:
          date=str(datetime.datetime.strptime(date, '%Y.%m.%d').date())
        else:
          date=str(datetime.datetime.strptime(date, '%d.%m.%Y').date())
    except ValueError:
        date=date
    
    return date