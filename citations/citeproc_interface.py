import citeproc
import lxml
from .dap_resource import DapResource
from .doi import DOIResource
import os

style_folder = '/home/griessbaum/Dropbox/UCSB/occur/styles-master/'


def list_styles():
    styles = os.listdir(style_folder)
    return styles


def dap2snippet(dap_url, style, resolve_dap_doi=True):
    reference = Reference()
    reference.from_dap(dap_url=dap_url, resolve_dap_doi=resolve_dap_doi)
    snippet = reference.to_snippet(style=style)
    return snippet


class Reference:

    def __init__(self):
        self.reference = citeproc.source.Reference(**{'key': 'refkey', 'type': 'dap resource'})
        self.errors = []

    def from_request(self, request):
        resolve_dap_doi = False
        if 'doiSource' in request.GET and request.GET['doiSource'] == 'das':
            resolve_dap_doi = True
        if 'dapUrl' in request.GET and request.GET['dapUrl'] is not '':
            self.from_dap(dap_url=request.GET['dapUrl'], resolve_dap_doi=resolve_dap_doi)
        if 'doi' in request.GET and request.GET['doi'] is not '' and not resolve_dap_doi:
            self.from_doi(doi=request.GET['doi'])

    def from_dap(self, dap_url, resolve_dap_doi=True):
        dap_resource = DapResource(dap_url=dap_url)
        reference = dap_resource.get_csl_reference(resolve_dap_doi)
        if reference is not None:
            self.reference = citeproc.source.Reference(**{**self.reference, **reference})
        self.errors.append(dap_resource.errors)

    def from_doi(self, doi):
        doi_resource = DOIResource(doi=doi)
        reference = doi_resource.get_csl_reference()
        if reference is not None:
            self.reference = citeproc.source.Reference(**{**self.reference, **reference})
        self.errors.append(doi_resource.errors)

    def to_snippet(self, style):
        try:
            style_file = os.path.join(style_folder, style)
            bib_style = citeproc.CitationStylesStyle(style=style_file, validate=True)
        except ValueError:
            return 'The style "{style}" is not available'.format(style=style)
        except lxml.etree.XMLSyntaxError:
            return 'The style "{style}" could not be processed'.format(style=style)
        bib_source = citeproc.source.BibliographySource()
        bib_source.add(self.reference)
        bibliography = citeproc.CitationStylesBibliography(bib_style, bib_source, citeproc.formatter.plain)
        citation = citeproc.Citation([citeproc.CitationItem('refkey')])
        bibliography.register(citation)
        if len(bibliography.bibliography()) > 0:
            cite_string = str(bibliography.bibliography()[0])
        else:
            cite_string = ''
        return cite_string

    def as_csl_json(self):
        return str(dict(self.reference)).replace('\'', '"')


