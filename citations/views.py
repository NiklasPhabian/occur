from django.http import HttpResponse
from django.utils import timezone
from .models import Citation
from .dap_resource import DapResource
from .doi import DOIResource

import os
import lxml


def stored(request):
    if 'page' not in request.GET:
        page = 1
    else:
        page = request.GET['page']
    citations = Citation.objects.order_by('-created_at')
    context = {'citations': citations, 'page': int(page), 'pages': range(1, 6)}
    return render(request=request, template_name='citations/stored.html', context=context)


def api(request):
    context = {}
    return render(request=request, template_name='citations/api.html', context=context)


def format(request):
    if 'dap_url' and 'style' in request.GET:
        return snippet(request)
    context = {'styles': styles(request, as_list=True)}
    return render(request=request, template_name='citations/format.html', context=context)


def dereference(request):
    context = {}
    if 'identifier' not in request.GET:
        return render(request=request, template_name='citations/dereference.html', context=context)

    identifier = request.GET['identifier'].strip()
    try:
        int(identifier)
        citation_matches = Citation.objects.filter(pk=identifier)
    except ValueError:
        try:
            dap_url = identifier.split('(')[0]
            created_at = identifier.split('(')[1].split(')')[0]
            citation_matches = Citation.objects.filter(dap_url=dap_url, created_at=created_at)
        except IndexError:
            context['error'] = '{identifier} does not appear to be a valid OCCUR identifier'.format(identifier=identifier)
            return render(request, template_name='citations/dereference.html', context=context)
    if len(citation_matches) == 0:
        context['error'] = 'No match for {identifier} found'.format(identifier=identifier)
        return render(request, template_name='citations/dereference.html', context=context)

    citation = citation_matches[0]
    dap_resource = DapResource(citation.dap_url)
    hash_remote = dap_resource.get_data_hash()
    hash_local = citation.data_hash
    if hash_remote == hash_local:
        return redirect(citation.dap_url)
    else:
        context['hash_local'] = hash_local
        context['hash_remote'] = hash_remote
        return render(request=request, template_name='citations/hash_mismatch.html', context=context)


def styles(request, as_list=False):
    styles = os.listdir('/usr/lib/python3/dist-packages/citeproc/data/styles')
    styles_out = []
    for style in styles:
        styles_out.append(style.replace('.csl', ''))
    if as_list:
        return styles_out
    else:
        return HttpResponse(', </br>'.join(styles_out))


def store(request):
    context = dict()
    if 'dap_url' not in request.GET:
        return render(request=request, template_name='citations/store.html', context=context)
    dap_url = request.GET['dap_url']
    citation = Citation()
    citation.dap_url = dap_url
    citation.add_resource()
    citation.add_data_hash()
    context['data_hash'] = citation.data_hash
    if citation.already_stored():
        citation = get_object_or_404(Citation, dap_url=dap_url)
        context['citation'] = citation
        return render(request=request, template_name='citations/already_stored.html', context=context)
    else:
        citation.created_at = timezone.now()
        citation.save()
        return redirect('citations:details', citation_id=citation.id)


def resolve_doi(request):
    context = {}
    if 'doi' not in request.GET:
        return render(request=request, template_name='citations/resolve_doi.html', context=context)
    doi = request.GET['doi']
    doi_resource = DOIResource(doi)
    doi_resource.download()
    return HttpResponse(doi_resource.csl_json)


def crosscite(request):
    if 'doi' and 'style' in request.GET:
        return snippet(request)
    context = {'styles': styles(request, as_list=True)}
    return render(request=request, template_name='citations/crosscite.html', context=context)


def stage(request):
    dap_url = request.GET['dap_url']
    citation = Citation()
    citation.dap_url = dap_url
    citation.add_resource()
    citation.dap_resource.get_citeproc()
    context = citation.dap_resource.citeproc.as_dict()
    return render(request=request, template_name='citations/stage.html', context=context)


def details(request, citation_id=None):
    if citation_id is not None:
        citation = get_object_or_404(Citation, pk=citation_id)
        citation.add_resource()
    elif request.GET['dap_url']:
        citation = Citation()
        citation.dap_url = request.GET['dap_url']
        citation.created_at = timezone.now()
        citation.add_resource()
        citation.dap_resource.get_data_hash()
    citation.dap_resource.get_citeproc()
    context = {'styles': styles(request, as_list=True),
               'citation': citation,
               'uid': citation.uid(),
               'bib': citation.dap_resource.citeproc.as_bibtex(),
               'csljson': citation.dap_resource.citeproc.as_csljson(),
               'das_url': citation.dap_resource.das_url,
               'dap_url': citation.dap_resource.dap_url,
               'data_hash': citation.dap_resource.data_hash}
    return render(request=request, template_name='citations/detail.html', context=context)


def bib(request):
    dap_url = request.GET['dap_url']
    cite_string = _snippet(dap_url=dap_url, style='bibtex')
    return HttpResponse(cite_string)


def csljson(request):
    dap_url = request.GET['dap_url']
    dap = DapResource(dap_url=dap_url)
    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_citeproc()

    return HttpResponse(str(bib_source))


def snippet(request):
    style = request.GET['style']
    if 'dap_url' in request.GET:
        dap_url = request.GET['dap_url']
        cite_string = _snippet(dap_url=dap_url, style=style)
    elif 'doi' in request.GET:
        doi = request.GET['doi']
        cite_string = _doi2snippet(doi=doi, style=style)
    return HttpResponse(cite_string)


# Not exposed
def _snippet(dap_url, style):
    dap = DapResource(dap_url=dap_url)
    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_citeproc()
    try:
        bib_style = citeproc.CitationStylesStyle(style=style, validate=False)
    except ValueError:
        return 'The style "{style}" is not available'.format(style=style)
    except lxml.etree.XMLSyntaxError:
        return 'The style "{style}" could not be processed'.format(style=style)
    bibliography = citeproc.CitationStylesBibliography(bib_style, bib_source, citeproc.formatter.plain)
    citation = citeproc.Citation([citeproc.CitationItem(bib_source.ref_key)])
    bibliography.register(citation)
    cite_string = str(bibliography.bibliography()[0])
    return cite_string


def _doi2snippet(doi, style):
    doi_ressource = DOIResource(doi)
    doi_ressource.download()
    print(doi_ressource.csl_json)
    bib_source = citeproc.source.json.CiteProcJSON(doi_ressource.csl_json)



    bib_style = citeproc.CitationStylesStyle(style=style, validate=False)
    bibliography = citeproc.CitationStylesBibliography(bib_style, bib_source, citeproc.formatter.plain)
    citation = citeproc.Citation([citeproc.CitationItem(bib_source.ref_key)])
    bibliography.register(citation)
    cite_string = str(bibliography.bibliography()[0])
    return cite_string
