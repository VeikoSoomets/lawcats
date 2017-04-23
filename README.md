Lawcats

http://www.oi.ut.ee/et/it-oigus/oigusrobootika-konkurss


**Installation instructions:**<br/>
- [Download and install Google Cloud SDK for Python](https://cloud.google.com/appengine/docs/standard/python/download)
- Install Python 2.7, PIP
- Install dependencies with PIP to libs/ folder by running: pip install -t libs/ -r requirements.txt'
<br/><br/>
**Instructions for running app:**<br/>
*Running App*
- Navigate to app folder and run 'dev_appserver.py . --storage_path=STORAGE_PATH --search_indexes_path=SEARCH_INDEXES_FILE_PATH'
<br/>

*Deploying App*
<br/>
appcfg.py update . -A directed-cove-374 -V 1
<br/><br/>
**Instructions for new languages:**<br/>
- Extract strings (make sure all files in main.mapping are UTF-8 without BOM):<br/>
pybabel extract -o locales/messages.pot -F main.mapping .<br/>
<br/>
- Generate lang file or if lang file exists, update:<br/>
pybabel init -l et -d locales -i locales/messages.pot<br/>
<br/>
- Update lang file:<br/>
pybabel update -l et -d locales -i locales/messages.pot<br/>
<br/>
- Edit files and compile:<br/>
pybabel compile -d locales<br/>
pybabel compile -l et -d locales -i locales/et/LC_MESSAGES/messages.po<br/>
<br/>
if operation is skipped because "catalogs are marked fuzzy"", then probably there might be mistakes with translations... if you are sure there are not, then remove line with fuzzy remarks from .po files (, fuzzy) and continue with operation