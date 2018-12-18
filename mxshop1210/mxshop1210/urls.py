from django.conf.urls import url,include
import xadmin
from mxshop1210.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from mx_goods.views import GoodsViewset,GoodsCategoryViewset,HotSearchViewset
from mx_user.views import SmsCodeViewsets,UserViewsets

router = DefaultRouter()
router.register(r'goods', GoodsViewset,base_name="goods")
router.register(r'categorys',GoodsCategoryViewset,base_name="categorys")
router.register(r"hotsearchs",HotSearchViewset,base_name="hotsearchs")
router.register(r'code',SmsCodeViewsets,base_name="code")
router.register(r'users',UserViewsets,base_name="users")















from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^', include(router.urls)),
    url(r'^login/', obtain_jwt_token),
]
