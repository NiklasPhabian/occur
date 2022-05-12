# OCCUR

<abbr title="OPeNDAP Citation Creator">OCCUR</abbr> is web service that creates identifiers and citations for data served by <abbr title="Open-source Project for a Network Data Access Protocol">OPeNDAP</abbr> servers. As a partial implementation of the <abbr title="Research Data Alliance">RDA</abbr> <abbr title="Working Group on Data Citation">WGDC</abbr> guidelines, it addresses the need to identify arbitrary subsets of revisable datasets. OCCUR creates and stores identifiers, which are a combination of the OPeNDAP query, the timestamp, and a hash of the query's result set. OCCUR can then de-reference these identifiers to access the data via OPeNDAP and to generate a human-readable citation snippet. When accessing data via the identifier, OCCUR compares the saved hash with the hash of the retrieved data, to determine whether the data has changed since it was cited. OCCUR uses CiteProc to generate citation snippets from the identifier's OPeNDAP query, timestamp, dataset-level metadata provided by the OPeNDAP server, and optionally the result set hash.

## How it works
OCCUR is a webservice that allows users to convert OPeNDAP queries into formatted citation snippets, much like www.crosscite.org provides a service for DOIs. OCCUR enables a user to retrieve and resolve citations from a datasource that is natively not capable of handling citations. OCCUR extracts the required metadata from the query and the metadata of the cited OPeNDAP resources, but also allows citations to be decorated with DOIs to associate external metadata to a dataset.

OCCUR further allows to create unique and fixed identities of data and subsets. This is achieved by OCCUR's ability to store citations. A stored citation can later be resolved through OCCUR, whereby OCCUR will verify that the data has not changed and therefore assures fixity. By storing citations at a central location, uniqueness can be negotiated: OCCUR will detect and merge citations to the exact same data.

## Background
Datasets may evolve over time through updates, appendation, or deletion [Klump2016]. We refer to these datasets as revisable data to delimit the term from datasets changing over time due to malicious manipulation or through data rot.

A revisable dataset is anticipated and intended to change its state over time. A citation system consequently has be able to distinguish between the states of a revisable dataset [Rauber2015, Klump2016]. To achieve this, merely the abstract state that a citation is referencing has to remain fixed (i.e. there cannot be ambiguity of the referenced state). This is true independently of the ability to de-reference a citation to the referenced state (i.e. the actual state being fixed).

Identifying and referencing an ephemeral state of a dataset is a necessary requirement for data citation. The ability to persistently retrieve these states however is a data publication challenge (not a data citation challange). It is hereby up to the publisher and repository to choose an apt level of zeal:

Pessimistic

  - Data is assumed to be ephemeral and consequently citations can never be de-referenced.
    
Optimistic
  - Data is assumed to be fixed. Citations always de-reference to the current state of the data.

Opportunistic
  - Data is assumed to remained fixed for some time. Citations can be de-referenced only until the data changes.

Pedantic
  - Every state of the data is saved. Consequently citations can always be de-referenced to the referenced state. OCCUR implements an opportunistic approach for the de-referencing of citations. While OCCUR guarantees citations to be unique and fixed, the referenced dataset may become unavailable (note: the referenced data cannot change since a citation is referencing a fixed state).

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
