lawcats

http://www.oi.ut.ee/et/it-oigus/oigusrobootika-konkurss


**Dependencies**:<br/>
google appengine,
bs4,
babel,
pytz  *(use gaepytz, it is faster),
feedparser
<br/><br/>
**Instructions for new languages:**<br/>
*Running App*
- Download and install google app engine sdk
- Navgiate to app folder and run 'dev_appserver.py .'
<br/>
*Deploying App*
appcfg.py update . -A directed-cove-374 -V 1
<br/><br/>
**Instructions for new languages:**<br/>
- Extract strings (make sure all files in main.mapping are UTF-8 without BOM):
pybabel extract -o locales/messages.pot -F main.mapping .
<br/>
- Generate lang file or if lang file exists, update:
pybabel init -l et -d locales -i locales/messages.pot

- Update lang file:
pybabel update -l et -d locales -i locales/messages.pot

- Edit files and compile:
pybabel compile -d locales
pybabel compile -l et -d locales -i locales/et/LC_MESSAGES/messages.po
<br/>
if operation is skipped because "catalogs are marked fuzzy"", then probably there might be mistakes with translations... if you are sure there are not, then remove line with fuzzy remarks from .po files (, fuzzy) and continue with operation