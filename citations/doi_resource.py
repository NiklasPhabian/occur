import requests
import json
from .citeproc_interface import Reference


class DOIResource:

    def __init__(self, doi):
        self.doi = str(doi).strip()
        self.doi_url = None
        self.csl_json = None
        self.valid_doi = True
        self.doi2url()
        self.error = None

    def doi2url(self):
        if str(self.doi[0:2]) == '10':
            self.doi_url = 'https://doi.org/' + self.doi
        elif str(self.doi[0:3]) == 'http':
            self.doi_url = self.doi
        else:
            self.doi_url = self.doi

    def download_csl_json(self):
        headers = {'Accept': 'application/vnd.citationstyles.csl+json'}
        try:
            ret = requests.get(self.doi_url, headers=headers, timeout=60)
            if ret.status_code == 200:
                self.csl_json = ret.text
            else:
                self.valid_doi = False
                self.error = 'Could not download CSL from DOI'
        except requests.exceptions.MissingSchema:
            self.valid_doi = False
            self.error = 'Could not download CSL from DOI; invalid DOI?'
        except requests.exceptions.Timeout:
            self.error = 'DOI CSL download timeout'
        if self.valid_doi:
            self.csl_json = json.loads(self.csl_json)
        else:
            self.csl_json = {}

    def to_reference(self):
        reference = Reference()
        reference.from_csl_json(self.csl_json)
        return reference


if __name__ == '__main__':
    doi = '10.1145/2783446.2783605'
    doi_resource = DOIResource(doi)
    doi_resource.download_csl_json()
    print(doi_resource.csl_json)
