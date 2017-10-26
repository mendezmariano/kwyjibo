import csv, random, string

from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.http import HttpResponse

from .models import *


class AbstractCsvFlattener(object):
    """AbstractCsvFlattener"""

    def header(self):
        pass

    def flatten(self, item):
        pass


class SequenceMaker(object):

    def __init__(self, maximum):
        super(SequenceMaker, self).__init__()
        self.counter = 0
        self.maximum = maximum

    def next(self):
        return_value = self.counter
        self.counter = (self.counter + 1) % self.maximum
        return return_value

class CsvExportService(object):
    """Utility for generating csv data exports."""
    def __init__(self):
        super(CsvExportService, self).__init__()
        self.seq = SequenceMaker(1000)

    def _random_string(self):
        name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(8))
        formatted_sequence = '%03.0f' % self.seq.next()
        return name + formatted_sequence

    def produce_response(self, queryset, flattener):
        filename = '%s.csv' % self._random_string()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        writer = csv.writer(response)
        writer.writerow(flattener.header())
        for item in queryset:
            writer.writerow(flattener.flatten(item))

        return response

