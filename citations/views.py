from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Citation
from .dap_resource import DapResource
import json
from .citeproc_interface import list_styles
from .citeproc_interface import Reference


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
    styles_out = []
    for style in list_styles():
        styles_out.append(style.replace('.csl', ''))
    if as_list:
        return styles_out
    if 'json' in request.GET:
        return HttpResponse(json.dumps(styles_out))
    return HttpResponse('' + '</br>'.join(styles_out) + '')


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
    dap_url = request.GET['dap_url']
    citation = Citation()
    citation.dap_url = dap_url
    citation.add_resource()
    citation.dap_resource.get_csl_source()

    context = citation.dap_resource.d
    reference = Reference()
    reference.from_dap(dap_url=citation.dap_url)

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
        citation.dap_resource.get_csl_source()
    reference = Reference()
    reference.from_dap(dap_url=citation.dap_url)
    bib = reference.to_snippet(style='bibtex')
    csl_json = reference.as_csl_json()
    context = {'styles': styles(request, as_list=True),
               'citation': citation,
               'uid': citation.uid(),
               'bib': bib,
               'csljson': csl_json,
               'das_url': citation.dap_resource.das_url,
               'dap_url': citation.dap_resource.dap_url,
               'data_hash': citation.dap_resource.data_hash}
    return render(request=request, template_name='citations/detail.html', context=context)


def format_citation(request):
    context = {}
    if 'dap_url' and 'doi' and 'style' in request.GET:
        reference = Reference()
        reference.from_request(request)
        citation_snippet = reference.to_snippet(style=request.GET['style'])
        return JsonResponse({'snippet': citation_snippet, 'error': ''})
    else:
        return render(request=request, template_name='citations/format.html', context=context)


def crosscite(request):
    context = {}
    if 'doi' and 'style' in request.GET:
        reference = Reference()
        reference.from_doi(request.GET['doi'])
        snippet = reference.to_snippet(style=request.GET['style'])
        return HttpResponse(snippet)
    return render(request=request, template_name='citations/crosscite.html', context=context)


def csljson(request):
    reference = Reference()
    reference.from_request(request)
    csl_json = reference.as_csl_json()
    return HttpResponse(csl_json)


def bib(request):
    reference = Reference()
    reference.from_request(request)
    cite_string = reference.to_snippet(style='bibtex')
    return HttpResponse(cite_string)

