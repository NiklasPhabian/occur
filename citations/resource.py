import hashlib
import requests
import re
import urllib.parse
import json
from citeproc_interface import Reference


class Resource:
    def __init__(self, url):
        self.url = url.strip()
        self.hash = None
        self.data = None
        self.errors = []
        self.dict = {'URL': self.url}

    def convert_to_dap(self):
        self.__class__ = DapResource
        self.bootstrap()

    def is_dap(self):
        self.convert_to_dap()
        if not self.das.exists():
            self.__class__ = Resource

    def download(self, headers=None):
        try:
            ret = requests.get(self.url, stream=True, headers=headers)
            if ret.status_code == 200:
                self.data = ret
            else:
                self.errors.append('could not download {url}'.format(url=self.url))
        except requests.exceptions.ConnectionError:
            self.errors.append('could not download {url}'.format(url=self.url))
        except requests.exceptions.InvalidSchema:
            self.errors.append('invalid schema in {url}'.format(url=self.url))
        except requests.exceptions.MissingSchema:
            self.url = 'http://' + self.url
            self.download()

    def get_hash(self):
        self.download()
        if self.data is None:
            return None
        else:
            hash_digest = hashlib.md5()
            for chunk in self.data:
                hash_digest.update(chunk)
            self.hash = hash_digest.hexdigest()
            return self.hash


class DapResource(Resource):

    def __init__(self, url):
        super(DapResource, self).__init__(url=url)
        self.base_url = None
        self.subset_parameters = None
        self.request_format = None
        self.das = None
        self.bootstrap()

    def bootstrap(self):
        self.parse_url()
        self.das = DasResource(url=self.url)

    def parse_url(self):
        components = urllib.parse.urlsplit(self.url)
        if components.scheme is None:
            self.url = 'http://' + self.url
        self.base_url = '.'.join(self.url.split('.')[:-1])
        self.subset_parameters = self.url.split('?')[-1]
        self.request_format = self.base_url.split('.')[-1]
        self.url = self.base_url + '.das'

    def to_dict(self):
        note = 'MD5 Hash: {hash}. Format: {request_format}'
        self.dict['note'] = note.format(hash=self.hash, request_format=self.request_format)
        self.dict['dimensions'] = self.subset_parameters
        return self.dict


class DasResource(Resource):

    def __init__(self, url):
        super(DasResource, self).__init__(url=url)
        self.doi = None

    def exists(self):
        if self.data is None:
            self.download()
        if self.data is not None:
            return True
        else:
            return False

    def to_dict(self):
        if self.data is None:
            self.download()
        global_dict = {}
        if 'global {' not in self.data.text.lower():
            print('no global section found')
            return global_dict
        global_section = re.split("global {", self.data.text, flags=re.IGNORECASE)[-1].split('}')[0]
        match = re.findall(u'[\n\r].*string *([^;]*)', global_section, re.IGNORECASE)
        if match is None:
            print('global section empty')
            return global_dict
        for entry in match:
            global_dict[entry.split(' "')[0]] = entry.split(' "')[1].replace('"', '')
        self.dict = global_dict
        return self.dict

    def extract_doi(self):
        if self.dict is None:
            self.to_dict()
        if 'DOI' in self.dict:
            self.doi = self.dict['DOI']

    def has_doi(self):
        if self.doi is not None:
            return True
        else:
            return False


class DOIResource(Resource):

    def __init__(self, doi):
        self.doi = doi.strip()
        self.doi2url()
        super(DOIResource, self).__init__(url=self.url)

    def doi2url(self):
        if str(self.doi[0:2]) == '10':
            self.url = 'https://doi.org/' + self.doi
        else:
            self.url = self.doi

    def download(self):
        headers = {'Accept': 'application/vnd.citationstyles.csl+json'}
        super(DOIResource, self).download(headers=headers)
        self.json = json.loads(self.data.text)

    def get_csl_source(self):
        self.download_csl()
        self.ref_data['id'] = 'refkey'
        self.ref_data['type'] = 'dataset'
        self.csl_source = CiteProcJSON2([self.ref_data])
        return self.csl_source

    def get_csl_reference(self):
        ref_key = 'refkey'
        self.get_csl_source()
        self.csl_reference = self.csl_source[ref_key]
        for key in self.csl_reference:
            if isinstance(self.csl_reference[key], citeproc.string.MixedString):
                self.csl_reference[key] = str(self.csl_reference[key])
        return self.csl_reference


def test_das():
    url = 'http://opendap.duckdns.org:8080/opendap/data/csv/temperature.csv.das'
    das = DasResource(url=url)
    print(das.to_dict())


def test_doi():
    doi = '10.1016/j.rse.2012.01.004'
    doi = DOIResource(doi)
    doi.download()
    print(doi.data.text)
    ref = Reference()
    ref.from_doi(doi)


def test_dap():
    url = 'http://opendap.duckdns.org:8080/opendap/data/csv/temprature.csv.ascii?Station[0:1:2],latitude[0:1:1]'
    extract_doi = True
    ref = Reference()
    r = Resource(url)
    r.get_hash()
    r.to_subtype()
    if type(r) == DapResource:
        ref.from_das(r.das)
        ref.from_dap(r)
        if extract_doi and r.das.has_doi():
            pass
    print(r.errors)
    print(ref.to_snippet('occur_verbose'))
    print(ref.as_csl_json())


if __name__ == '__main__':
    test_das()
    test_doi()




