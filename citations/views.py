from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Citation
from .dap_resource import DapResource
import citeproc
import os


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
    if 'dap_url' and 'format' in request.GET:
        return snippet(request)
    context = {'styles': styles(request, as_list=True)}
    return render(request=request, template_name='citations/format.html', context=context)


def dereference(request):
    context = {}
    if 'identifier' not in request.GET:
        context = {}
        return render(request=request, template_name='citations/dereference.html', context=context)
    else:
        identifier = request.GET['identifier']
        try:
            int(identifier)
            citation_matches = Citation.objects.filter(pk=identifier)
        except ValueError:
            citation_matches = Citation.objects.filter(dap_url=identifier)
        if len(citation_matches) == 0:
            return HttpResponse('no match found')
        else:
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


def stage(request):
    context = {}
    dap_url = request.GET['dap_url']
    citation = Citation()
    citation.dap_url = dap_url
    citation.add_resource()
    citation.dap_resource.get_citeproc()
    context = citation.dap_resource.citeproc.as_dict()
    print(context)
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
    cite_string = _snippet(dap_url=dap_url, format='bibtex')
    return HttpResponse(cite_string)


def csljson(request):
    dap_url = request.GET['dap_url']
    dap = DapResource(dap_url=dap_url)
    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_citeproc()
    return HttpResponse(str(bib_source))


def snippet(request):
    dap_url = request.GET['dap_url']
    format = request.GET['format']
    cite_string = _snippet(dap_url=dap_url, format=format)
    return HttpResponse(cite_string)


# Not exposed
def _snippet(dap_url, format):
    dap = DapResource(dap_url=dap_url)
    dap.get_das()
    dap.get_data_hash()
    bib_source = dap.get_citeproc()

    bib_style = citeproc.CitationStylesStyle(format, validate=False)
    bibliography = citeproc.CitationStylesBibliography(bib_style, bib_source, citeproc.formatter.plain)
    citation = citeproc.Citation([citeproc.CitationItem(bib_source.ref_key)])
    bibliography.register(citation)
    cite_string = str(bibliography.bibliography()[0])
    return cite_string