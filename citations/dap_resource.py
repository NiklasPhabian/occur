import re
import requests
import hashlib
from .citeproc_interface import Reference


class DapResource:
    def __init__(self, dap_url):
        self.dap_url = dap_url.strip()
        self.base_url = None
        self.subset_parameters = None
        self.request_format = None
        self.query = None
        self.data_hash = None
        self.das_url = None
        self.das_txt = ''
        self.das = None
        self.doi = None
        self.error = None
        self.reference_dict = None
        self.parse_url()

    def parse_url(self):
        if self.dap_url[0:4] != 'http':
            self.dap_url = 'http://' + self.dap_url
        self.base_url = '.'.join(self.dap_url.split('.')[:-1])
        if '?' in self.dap_url:
            self.subset_parameters = self.dap_url.split('?')[-1]
        else:
            self.subset_parameters = ''
        self.request_format = self.base_url.split('.')[-1]
        self.das_url = self.base_url + '.das'
        self.query = self.dap_url.split('/')[-1]

    def get_das(self):
        try:
            ret = requests.get(self.das_url)
            if ret.status_code == 200:
                self.das_txt = ret.text
            else:
                self.error = 'DAS could not be downloaded'
        except requests.exceptions.ConnectionError:
            self.error = 'DAS could not be downloaded'
        except requests.exceptions.InvalidSchema:
            self.error = 'DAS could not be downloaded'
        except requests.exceptions.MissingSchema:
            self.error = 'DAS could not be downloaded'
        except requests.exceptions.Timeout:
            self.error = 'DAS could not be downloaded'
        self.das = DAS(self.das_txt)

    def get_doi(self):
        if 'DOI' in self.das.global_dict:
            self.doi = self.das.global_dict['DOI']
        return self.doi

    def get_data_hash(self):
        try:
            ret = requests.get(self.dap_url, stream=True)
        except requests.exceptions.ConnectionError:
            self.error = 'Could not download resource; Connection Error'
            ret = ''
        except requests.exceptions.InvalidSchema:
            self.error = 'Could not download resource; invalid URL?'
            ret = ''
        except requests.exceptions.InvalidURL:
            self.error = 'Could not download resource; invalid URL?'
            ret = ''
        except requests.exceptions.Timeout:
            self.error = 'Could not download resource; invalid URL?'
            ret = ''
        hash_digest = hashlib.md5()
        for chunk in ret:
            hash_digest.update(chunk)
        self.data_hash = hash_digest.hexdigest()
        return self.data_hash

    def add_container_title(self, container_title):
        self[self.ref_key]['container_title'] = container_title

    def to_reference_dict(self):
        self.reference_dict = self.das.global_dict
        self.reference_dict['dimensions'] = self.subset_parameters
        self.reference_dict['URL'] = self.dap_url
        self.reference_dict['note'] = 'MD5 Hash: {hash}'.format(hash=self.data_hash)
        self.reference_dict['container_title'] = self.request_format
        return self.reference_dict

    def to_reference(self):
        reference_dict = self.to_reference_dict()
        reference = Reference()
        reference.from_dict(reference_dict)
        return reference


class DAS:
    def __init__(self, das):
        self.global_dict = {}
        self.parse(das)

    def __str__(self):
        return self.global_dict

    def parse(self, das):
        if 'global {' not in das.lower():
            print('no global section found')
            return self.global_dict
        global_section = re.split("global {", das, flags=re.IGNORECASE)[-1].split('}')[0]
        match = re.findall(u'[\n\r].*string *([^;]*)', global_section, re.IGNORECASE)
        if match is None:
            print('global section empty')
            return self.global_dict
        for entry in match:
            self.global_dict[entry.split(' "')[0]] = entry.split(' "')[1].replace('"', '')
        return self.global_dict


if __name__ == '__main__':
    dap = DapResource('https://ladsweb.modaps.eosdis.nasa.gov/opendap/LandSeaMask_DEM/6/dem15ARC_E0N0.hdf.ascii?Elevation[0:1:1][0:1:1]')
    dap = DapResource('http://opendap.duckdns.org:8080/opendap/data/csv/temperature.csv.ascii?Station[0:1:2],latitude[0:1:1](2018-09-10 20:58) ')

    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_csl_source()
    snippet = bib_source.as_snippet('occur')
    bib_source.as_csljson()
    print(snippet)





