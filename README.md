lawcats

http://www.oi.ut.ee/et/it-oigus/oigusrobootika-konkurss


***Dependencies***:<br/>
bs4,
babel,
pytz  *(use gaepytz, it is faster),
feedparser


*Instructions for new languages:*
... first navigate to project folder in cmd or shell

1) Extract strings (make sure all files in main.mapping are UTF-8 without BOM): 

  pybabel extract -o locales/messages.pot -F main.mapping .

2) Generate lang file or if lang file exists, update:

generate: 
pybabel init -l et -d locales -i locales/messages.pot

update: 
pybabel update -l et -d locales -i locales/messages.pot

3) edit files and compile:
-- pybabel compile -d locales

pybabel compile -l et -d locales -i locales/et/LC_MESSAGES/messages.po


if operation is skipped because "catalogs are marked fuzzy"", then probably there might be mistakes with translations... if you are sure there are not, then remove line with fuzzy remarks from .po files (, fuzzy) and continue with operation

