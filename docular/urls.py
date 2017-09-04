from django.conf.urls import include, url

from docular.structure.routes import router
from docular.structure.views import NestedDetail


def match(name):
    return '(?P<{0}>[a-zA-Z0-9_-]+)'.format(name)


urlpatterns = [
    # /akn/us/cfr/title_12/part_1005/@2011-31725/ecfr/~part_1005__subpart_A.json
    url('^akn/us'
        '/' + match('doc_type') +           # cfr
        '/' + match('doc_subtype') +        # title_12
        '/' + match('work_id') +            # part_1005
        '/@' + match('expression_id') +     # 2011-31725
        '/' + match('author') +             # ecfr
        '/~' + match('label'),              # part_1005__subpart_A
        NestedDetail.as_view()),
    url('^', include(router.urls)),
]
