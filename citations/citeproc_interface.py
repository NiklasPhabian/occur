import citeproc
import lxml
import os

style_folder = '/home/griessbaum/Dropbox/UCSB/data_citation/occur/styles-master/'


def list_styles():
    styles = os.listdir(style_folder)
    return styles


def dap2snippet(dap_url, style, resolve_dap_doi=True):
    reference = Reference()
    reference.from_dap(dap_url=dap_url, resolve_dap_doi=resolve_dap_doi)
    snippet = reference.to_snippet(style=style)
    return snippet


class CiteProcDict(citeproc.source.bibtex.BibTeX):

    def __init__(self, das):
        self.preamble_macros = {}
        ref_data = {}
        for key, value in das.items():
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
                    ref_data[python_key] = value
            else:
                print('{} is not a citproc variable'.format(python_key))

        if self._bibtex_to_csl_date(das) is not None:
            ref_data['issued'] = self._bibtex_to_csl_date(das)
        ref_type = 'dap resource'
        reference = citeproc.source.Reference('refkey', ref_type, **ref_data)
        self.add(reference)


class CiteProcDAS(CiteProcDict):
    pass


class Reference(citeproc.source.Reference):

    def __init__(self):
        self.key = 'refkey'
        self.errors = None

    def from_dict(self, dict):
        source = CiteProcDict(dict)
        self.update(source['refkey'])

    def from_csl_json(self, csl_json):
        csl_json['id'] = 'refkey'
        csl_json['type'] = 'dataset'
        source = citeproc.source.json.CiteProcJSON([csl_json])
        self.update(source['refkey'])

    def to_snippet(self, style):
        if style == '':
            self.errors = 'No style specified'
            return None
        try:
            style_file = os.path.join(style_folder, style)
            bib_style = citeproc.CitationStylesStyle(style=style_file, validate=False)
        except AttributeError:
            self.errors = 'The style "{style}" is not available'.format(style=style)
            return None
        except lxml.etree.XMLSyntaxError:
            self.errors = 'The style "{style}" could not be processed'.format(style=style)
            return None
        bib_source = citeproc.source.BibliographySource()
        bib_source.add(self)
        bibliography = citeproc.CitationStylesBibliography(bib_style, bib_source, citeproc.formatter.plain)
        citation = citeproc.Citation([citeproc.CitationItem('refkey')])
        bibliography.register(citation)
        if len(bibliography.bibliography()) > 0:
            snippet = str(bibliography.bibliography()[0])
        else:
            snippet = None
        return snippet

    def as_csl_json(self):
        return str(dict(self)).replace('\'', '"')

    def merge(self, other):
        self.update(other)
