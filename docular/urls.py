from django.conf.urls import url

from docular.layer.views import get


def match(name):
    return '(?P<{0}>[a-zA-Z0-9_-]+)'.format(name)


urlpatterns = [
    # /akn/us/cfr/title_12/part_1005/@2011-31725/~part_1005__subpart_A.json
    url('^akn/us'
        '/' + match('doc_type') +           # cfr
        '/' + match('doc_subtype') +        # title_12
        '/' + match('work_id') +            # part_1005
        '/@' + match('entity_id') +         # 2011-31725
        '/~' + match('label') +             # part_1005__subpart_A
        r'\.' + match('fmt'),               # json
        get),
]
