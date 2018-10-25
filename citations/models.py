from django.db import models
from .dap_resource import DapResource


class Citation(models.Model):
    dap_url = models.URLField(max_length=200)
    data_hash = models.CharField(max_length=32)
    created_at = models.DateTimeField(blank=True)

    def add_resource(self):
        self.dap_resource = DapResource(self.dap_url)

    def url_already_stored(self):
        queryset = Citation.objects.filter(dap_url=self.dap_url)
        if queryset.count() > 0:
            return True
        else:
            return False

    def already_stored(self):
        queryset = Citation.objects.filter(dap_url=self.dap_url, data_hash=self.data_hash)
        if queryset.count() > 0:
            return True
        else:
            return False

    def citation_id(self):
        queryset = Citation.objects.filter(dap_url=self.dap_url)
        if queryset.count() > 0:
            return queryset[0].id
        else:
            return None

    def get_pk(self):
        return self.id

    def add_data_hash(self):
        self.data_hash = self.dap_resource.get_data_hash()

    def uid(self):
        return self.dap_url + '(' + str(self.created_at.replace(tzinfo=None)) + ')'

    def __str__(self):
        return str(self.dap_url)


class CitationExtended(Citation):
    title = models.CharField(max_length=200, default=None)
    author = models.CharField(max_length=200, default=None)
    institution = models.CharField(max_length=200, default=None)
    doi = models.CharField(max_length=200, default=None)
    data = models.FileField(upload_to='media/', default=None)
    comment = models.TextField(default=None)


class CitationMetaData(models.Model):
    citation_pk = models.IntegerField()
    doi = models.CharField(max_length=200)


