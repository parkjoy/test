from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import mixins
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from mx_user.serializer import SmsSerializers,UserRegSerializer
from utils.yunpian import YunPian
from mxshop1210.settings import API_KEY
from mx_user.models import VerifyCode,UserProfile
from rest_framework_jwt.serializers import jwt_payload_handler,jwt_encode_handler
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from random import choice

#自定义用户认证  添加手机号认证
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewsets(viewsets.GenericViewSet,mixins.CreateModelMixin):
    """
    create: 
        发送短信
    """
    serializer_class = SmsSerializers

    # 生成四位数的验证码
    def generate_code(self):
        sends = '1234567890'
        radmon_str = []
        for i in range(4):
            radmon_str.append(choice(sends))
        return ''.join(radmon_str)

    # 重写create  和form表单验证一样
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # 校验错误，抛出异常
        serializer.is_valid(raise_exception=True)
        # 获取用户输入的内容
        mobile = request.data['mobile']
        # 发送验证码
        yunpian = YunPian(API_KEY)
        code = self.generate_code()
        sms_status = yunpian.send_sms(code=code, mobile=mobile)
        # 0代表发送成功，其他code代表出错

        if sms_status['code'] != 0:
            return Response({
                'mobile': sms_status['msg']
            }, status=status.HTTP_400_BAD_REQUEST)

        else:
            # 发送成功，创建表
            verify_code = VerifyCode(code=code, mobile=mobile)
            verify_code.save()
            # HTTP_201_CREATED  创建
            return Response({
                'mobile': mobile
            }, status=status.HTTP_201_CREATED)


class UserViewsets(viewsets.GenericViewSet,mixins.CreateModelMixin):
    """
    create:
        创建用户
    """
    # 序列化器
    serializer_class = UserRegSerializer
    #获取所有的用户表
    queryset = UserProfile.objects.all()
    # 用户认证
    authentication_classes = (SessionAuthentication, JSONWebTokenAuthentication)

    # 动态获取序列化  根据请求返回不同的序列化结果
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserRegSerializer
        return UserDetailSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            # 用户权限  注册不需要登录  进入用户中心 需要登录  动态配置
            return [IsAuthenticated()]
        # 注册不需要验证用户是否登录
        elif self.action == 'create':
            return []
        return []

    # 生成token返回
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 接收刚刚登录的用户对象
        user = self.perform_create(serializer)

        # =====token的定制化
        # 获取返回序列化后要的对象
        re_dict = serializer.data
        # 给登录的用户对象添加token信息
        payload = jwt_payload_handler(user)
        # 给返回的对象添加token信息
        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['name'] = user.name if user.name else user.username
        # ====结束
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 重写 APIView获取详细信息
    def get_object(self):
        # 获取当前登录的用户
        return self.request.user