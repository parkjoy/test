# coding=utf-8
from rest_framework import serializers

from mx_goods.models import Goods,GoodsCategory,HotSearchWords

class GoodsCategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"

class GoodsCategorySerializer2(serializers.ModelSerializer):
    sub_cat = GoodsCategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"

#分类
class GoodsCategorySerializer(serializers.ModelSerializer):
    sub_cat = GoodsCategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


#商品列表
class GoodsSerializer(serializers.ModelSerializer):
    category = GoodsCategorySerializer()
    class Meta:
        model = Goods
        fields = "__all__"


#热搜词
class HotSearchSeriailzer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = ("keywords",)