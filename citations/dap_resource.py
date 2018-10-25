import re
import requests
import hashlib
import citeproc
from .doi import DOIResource


class DapResource:
    def __init__(self, dap_url):
        self.dap_url = dap_url.strip()
        self.base_url = None
        self.subset_parameters = None
        self.request_format = None
        self.das_url = None
        self.query = None
        self.data_hash = None
        self.das = None
        self.doi = None
        self.csl_source = None
        self.csl_reference = None
        self.errors = None
        self.parse_url()

    def parse_url(self):
        if self.dap_url[0:4] != 'http':
            self.dap_url = 'http://' + self.dap_url
        self.base_url = '.'.join(self.dap_url.split('.')[:-1])
        self.subset_parameters = self.dap_url.split('?')[-1]
        self.request_format = self.base_url.split('.')[-1]
        self.das_url = self.base_url + '.das'
        self.query = self.dap_url.split('/')[-1]

    def get_das(self):
        try:
            ret = requests.get(self.das_url)
            if ret.status_code == 200:
                self.das = ret.text
            else:
                self.errors = 'das could not be downloaded'
        except requests.exceptions.ConnectionError:
            self.errors = 'das could not be downloaded'
        except requests.exceptions.InvalidSchema:
            self.errors = 'das could not be downloaded'

    def get_doi(self):
        if self.csl_reference is None:
            self.get_csl_reference()
        if 'DOI' in self.csl_reference:
            self.doi = self.csl_reference['DOI']
        return self.doi

    def get_data_hash(self):
        try:
            ret = requests.get(self.dap_url, stream=True)
        except requests.exceptions.ConnectionError:
            ret = ''
        except requests.exceptions.InvalidSchema:
            ret = ''
        hash_digest = hashlib.md5()
        for chunk in ret:
            hash_digest.update(chunk)
        self.data_hash = hash_digest.hexdigest()
        return self.data_hash

    def get_csl_source(self):
        if self.das is None:
            self.get_das()
        if self.data_hash is None:
            self.get_data_hash()
        if self.das is not None:
            self.csl_source = CiteProcDAS(self.das)
            self.csl_source.add_url(self.dap_url)
            self.csl_source.add_hash(self.data_hash)
            self.csl_source.add_dimensions(self.subset_parameters)
        return self.csl_source

    def get_csl_reference(self, resolve_dap_doi=False):
        if self.csl_source is None:
            self.get_csl_source()
        if self.csl_source is not None:
            reference = self.csl_source['refkey']
            if resolve_dap_doi:
                if self.doi is None:
                    self.get_doi()
                doi_resource = DOIResource(self.doi)
                doi_reference = doi_resource.get_csl_reference()
                reference = {**reference, **doi_reference}
            self.csl_reference = citeproc.source.Reference(**reference)
        return self.csl_reference


class CiteProcDAS(citeproc.source.bibtex.BibTeX):

    def __init__(self, das):
        self.ref_key = 'refkey'
        das_json = self.das2dict(das)
        self.preamble_macros = {}
        ref_data = {}
        for key, value in das_json.items():
            python_key = key.replace('-', '_')
            if python_key == 'id':
                continue
            elif python_key in ['month', 'year']:
                continue
            if python_key in citeproc.NAMES:
                value = self._parse_author(authors=value)
            elif python_key in citeproc.DATES:
                value = self.parse_date(value)
            if python_key in citeproc.VARIABLES:
                if type(value) is str:
                    ref_data[python_key] = value.replace('\n', '')
            else:
                print('{} is not a citproc variable'.format(python_key))

        if self._bibtex_to_csl_date(das_json) is not None:
            ref_data['issued'] = self._bibtex_to_csl_date(das_json)
        ref_type = 'dap resource'
        reference = citeproc.source.Reference(self.ref_key, ref_type, **ref_data)
        self.add(reference)

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

    def das2dict(self, das):
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
        csl_json = []
        for key in self:
            csl_json.append(dict(self['refkey']))
        return csl_json

    def as_dict(self):
        return self[self.ref_key]


if __name__ == '__main__':
    dap = DapResource('https://ladsweb.modaps.eosdis.nasa.gov/opendap/LandSeaMask_DEM/6/dem15ARC_E0N0.hdf.ascii?Elevation[0:1:1][0:1:1]')
    dap = DapResource('http://opendap.duckdns.org:8080/opendap/data/csv/temperature.csv.ascii?Station[0:1:2],latitude[0:1:1](2018-09-10 20:58) ')

    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_csl_source()
    snippet = bib_source.as_snippet('occur')
    bib_source.as_csljson()
    print(snippet)





