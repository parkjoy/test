from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from mx_goods.models import Goods,GoodsCategory,HotSearchWords
from mx_goods.serializer import GoodsSerializer,GoodsCategorySerializer,HotSearchSeriailzer
from mx_goods.filter import GoodsListFilter





class GoodsPagination(PageNumberPagination):
    """
    分页
    """
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class GoodsViewset(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    list:
        商品列表
    retrieve:
        商品详情
    """
    queryset = Goods.objects.all()
    pagination_class = GoodsPagination
    serializer_class = GoodsSerializer
    filter_backends = (filters.SearchFilter,filters.OrderingFilter,DjangoFilterBackend)
    filterset_class = GoodsListFilter
    search_fields = ("name", "goods_brief", "goods_desc")
    ordering_fields = ("sold_num", "shop_price")


class GoodsCategoryViewset(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    list:
        分类列表
    retrieve:
        分类详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = GoodsCategorySerializer



class HotSearchViewset(viewsets.GenericViewSet,mixins.ListModelMixin):
    """
    list:
        热搜词
    """
    queryset = HotSearchWords.objects.all().order_by('-index')[:5]
    serializer_class = HotSearchSeriailzer
