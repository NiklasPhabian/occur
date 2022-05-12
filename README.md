# OCCUR

<abbr title="OPeNDAP Citation Creator">OCCUR</abbr> is web service that creates identifiers and citations for data served by <abbr title="Open-source Project for a Network Data Access Protocol">OPeNDAP</abbr> servers. As a partial implementation of the <abbr title="Research Data Alliance">RDA</abbr> <abbr title="Working Group on Data Citation">WGDC</abbr> guidelines, it addresses the need to identify arbitrary subsets of revisable datasets. OCCUR creates and stores identifiers, which are a combination of the OPeNDAP query, the timestamp, and a hash of the query's result set. OCCUR can then de-reference these identifiers to access the data via OPeNDAP and to generate a human-readable citation snippet. When accessing data via the identifier, OCCUR compares the saved hash with the hash of the retrieved data, to determine whether the data has changed since it was cited. OCCUR uses CiteProc to generate citation snippets from the identifier's OPeNDAP query, timestamp, dataset-level metadata provided by the OPeNDAP server, and optionally the result set hash.

## Install / Deploy

```bash
mkvirtualenv occur
pip3 install django requests citeproc-py
python3 manage.py migrate
```

add entry to settings.py:

```
ALLOWED_HOSTS = ['occur.duckdns.org', '127.0.0.1']
```

```bash
python3 manage.py runserver 127.0.0.1:8000
```
