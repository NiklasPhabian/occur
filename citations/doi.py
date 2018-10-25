import requests
import json
import citeproc


class CiteProcJSON2(citeproc.source.json.CiteProcJSON):

    def as_csljson(self):
        csl_json = []
        for refkey in self:
            reference = dict(self[refkey])
            for key in reference:
                if isinstance(reference[key], citeproc.string.MixedString):
                    reference[key] = str(reference[key])
            csl_json.append(reference)
        return csl_json

    def __str__(self):
        return str(self.as_csljson())


class DOIResource:

    def __init__(self, doi):
        self.doi = doi.strip()
        self.doi_url = None
        self.csl_json = None
        self.csl_reference = None
        self.csl_source = None
        self.ref_data = None
        self.valid_doi = True
        self.errors = None
        self.doi2url()

    def doi2url(self):

        if str(self.doi[0:2]) == '10':
            self.doi_url = 'https://doi.org/' + self.doi
        elif str(self.doi[0:3]) == 'http':
            self.doi_url = self.doi
        else:
            self.doi_url = self.doi

    def download_csl(self):
        headers = {'Accept': 'application/vnd.citationstyles.csl+json'}
        try:
            ret = requests.get(self.doi_url, headers=headers)
            if ret.status_code == 200:
                self.csl_json = ret.text
            else:
                self.valid_doi = False
        except requests.exceptions.MissingSchema:
            self.valid_doi = False
        if self.valid_doi:
            self.ref_data = json.loads(self.csl_json)
        else:
            self.ref_data = {}

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





