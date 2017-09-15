from rest_framework import routers

from docular.structure.views import DocStructViewSet

router = routers.DefaultRouter()
router.register('doc_struct', DocStructViewSet)
