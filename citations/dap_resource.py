import re
import requests
import hashlib
import citeproc


class DapResource:
    def __init__(self, dap_url):
        self.dap_url = dap_url
        self.base_url = None
        self.subset_parameters = None
        self.request_format = None
        self.das_url = None
        self.query = None
        self.data_hash = None
        self.parse_url()
        self.das = None
        self.citeproc = None

    def parse_url(self):
        self.base_url = '.'.join(self.dap_url.split('.')[:-1])
        self.subset_parameters = self.dap_url.split('?')[-1]
        self.request_format = self.base_url.split('.')[-1]
        self.das_url = self.base_url + '.das'
        self.query = self.dap_url.split('/')[-1]

    def get_das(self):
        self.das = requests.get(self.das_url).text

    def get_data_hash(self):
        ret = requests.get(self.dap_url, stream=True)
        hash_digest = hashlib.md5()
        for chunk in ret:
            hash_digest.update(chunk)
        self.data_hash = hash_digest.hexdigest()
        return self.data_hash

    def get_citeproc(self):
        if self.das is None:
            self.get_das()
        self.citeproc = CiteProcDAS(self.das)
        self.citeproc.add_url(self.dap_url)
        self.citeproc.add_hash(self.data_hash)
        self.citeproc.add_dimensions(self.subset_parameters)
        return self.citeproc


class CiteProcDAS(citeproc.source.bibtex.BibTeX):

    def __init__(self, das):
        self.ref_key = 'refkey'
        das_json = self.das2dict(das)
        self.preamble_macros = {}
        ref_data = {}
        for key, value in das_json.items():
            python_key = key.replace('-', '_')
            if python_key == 'id':
                self.ref_key = 'dap'
                continue
            elif python_key in ['month', 'year']:
                continue
            if python_key in citeproc.NAMES:
                value = self._parse_author(authors=value)
            elif python_key in citeproc.DATES:
                value = self.parse_date(value)
            if python_key in citeproc.VARIABLES:
                ref_data[python_key] = value
            else:
                print('{} is not a citproc variable'.format(python_key))
        ref_data['issued'] = self._bibtex_to_csl_date(das_json)
        ref_type = 'dap resource'
        self.add(citeproc.source.Reference(self.ref_key, ref_type, **ref_data))

    @staticmethod
    def das2dict(das):
        global_dict = {}
        if 'global {' not in das.lower():
            print('no global section found')
            return global_dict
        global_section = re.split("global {", das, flags=re.IGNORECASE)[-1].split('}')[0]
        match = re.findall(u'[\n\r].*string *([^;]*)', global_section, re.IGNORECASE)
        if match is None:
            print('global section empty')
            return global_dict
        for entry in match:
            global_dict[entry.split(' "')[0]] = entry.split(' "')[1].replace('"', '')
        return global_dict

    def as_csljson(self):
        csl_json = dict(self[self.ref_key])
        if csl_json['issued'] is not None:
            year = str(csl_json['issued']['year'])
            month = str(csl_json['issued']['month'])
            issued_str = {'date-parts': [[year, month]]}
            csl_json['issued'] = issued_str
        csl_json = str(csl_json).replace('\'', '"')
        return '[' + str(csl_json) + ']'

    def as_bibtex(self):
        return self.as_snippet(cite_format='bibtex')

    def as_dict(self):
        return self[self.ref_key]

    def __str__(self):
        return self.as_csljson()

    def add_container_title(self, container_title):
        self[self.ref_key]['container_title'] = container_title

    def add_url(self, url):
        self[self.ref_key]['URL'] = url

    def add_hash(self, hash):
        self[self.ref_key]['note'] = 'MD5 Hash: {hash}'.format(hash=hash)

    def add_dimensions(self, dimensions):
        self[self.ref_key]['dimensions'] = dimensions

    def as_snippet(self, cite_format):
        bib_style = citeproc.CitationStylesStyle(cite_format, validate=False)
        bibliography = citeproc.CitationStylesBibliography(bib_style, self, citeproc.formatter.plain)
        citation = citeproc.Citation([citeproc.CitationItem(self.ref_key)])
        bibliography.register(citation)
        cite_string = str(bibliography.bibliography()[0])
        return cite_string


if __name__ == '__main__':
    dap = DapResource('https://ladsweb.modaps.eosdis.nasa.gov/opendap/LandSeaMask_DEM/6/dem15ARC_E0N0.hdf.ascii?Elevation[0:1:1][0:1:1]')
    dap = DapResource('http://opendap.duckdns.org:8080/opendap/data/csv/temperature.csv.ascii?Station[0:1:2],latitude[0:1:1](2018-09-10 20:58) ')

    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_citeproc()
    snippet = bib_source.as_snippet('occur')
    bib_source.as_csljson()
    print(snippet)





