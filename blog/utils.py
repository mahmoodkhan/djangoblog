from django.core.serializers.python import Serializer
from django.utils.encoding import smart_text
class JsonSerializer(Serializer):
    """
    Overrides django's JSON serialzer so that the JSON output is more flat.

    http://www.acnenomor.com/2673377p1/django-serializers-to-json-custom-json-output-format
    Usage:
        serializer = JsonSerializer()
        data = serializer.serialize(<queryset>, <optional>fields=('field1', 'field2'))
    """
    def end_object( self, obj ):
        #self._current['id'] = obj._get_pk_val()
        self._current['id'] = smart_text(obj._get_pk_val(), strings_only=True)
        self.objects.append( self._current )