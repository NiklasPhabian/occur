import requests
import json


class DOIResource:

    def __init__(self, doi):
        self.doi = doi
        self.csl_json = [{}]

    def download(self):
        headers = {'Accept': 'application/vnd.citationstyles.csl+json'}
        ret = requests.get(self.doi, headers=headers)
        self.csl_json = [json.loads(ret.text)]
        return self.csl_json

