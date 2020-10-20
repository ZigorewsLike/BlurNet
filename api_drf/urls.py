from rest_framework import routers
from .views import FileViewSet, BlurViewSet

router = routers.DefaultRouter()
router.register('blurImg', FileViewSet)
router.register('blurAnn', BlurViewSet)

urlpatterns = router.urls
