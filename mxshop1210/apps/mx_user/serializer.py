# coding=utf-8
from rest_framework import serializers
from rest_framework import serializers
from mx_user.models import VerifyCode
from mx_user.models import UserProfile
from mxshop1210.settings import REGEX_MOBILE
import re
from datetime import datetime
from datetime import timedelta

from rest_framework.validators import UniqueValidator

# 验证码
class SmsSerializers(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """ 
        验证手机号       
        """
        # 1:手机号是否注册过
        if UserProfile.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")
        # 2：手机号是否输入合法
        elif not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号输入非法")
        # 3：验证发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        # 16:30        # 16:29        # 16.29:30
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")
        return mobile


#验证用户
class UserRegSerializer(serializers.ModelSerializer):
    #write_only=True,  不会序列化该字段
    code = serializers.CharField(required=True,max_length=4,min_length=4,write_only=True,
                                 help_text='验证码',label='验证码',
                                 error_messages={
                                     'blank':'请输入验证码',
                                     'max_length':'验证码过长错误',
                                     'min_length':'验证码过短错误',
                                 })

    #验证username是否存在
    username = serializers.CharField(max_length=11,min_length=11,allow_blank=False,required=True,label='用户名',
                                     help_text='用户名',
                                     error_messages={
                                         'blank': '请输入用户名',
                                         'max_length': '用户名超过最大长度',
                                         'min_length': '用户名最少11位',
                                     },
                                     validators=[UniqueValidator(queryset=UserProfile.objects.all(),message='用户已经存在')]
                                     )

    #密码默认是明文  但是django中密码加密
    password = serializers.CharField(label='密码',write_only=True,help_text='密码',
        style={'input_type': 'password'}
    )

    # def create(self, validated_data):
    #     # modelserializer已经重载了create这个方法，所以重载需要重写    #获取了user对象
    #     user = super(UserRegSerializer, self).create(validated_data = validated_data)
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user

    #验证字段validate_code
    def validate_code(self, code):
        #获取验证码
        verify_recode = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if verify_recode:
            #获取最后的验证码 发送2次验证码已最后一次验证码为主
            last_recode = verify_recode[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_recode.add_time:
                raise serializers.ValidationError('验证码过期')
            if last_recode.code != code:
                raise serializers.ValidationError('验证码错误')
        # 2：验证码不存在
        else:
            raise serializers.ValidationError('验证码不存在')

    #操控数据 字段处理
    def validate(self, attrs):
        attrs['mobile'] = attrs['username']
        #删除不用的字段code
        del attrs['code']
        #将数据返回
        return attrs

    #username  登录时需要这个字段  但是注册的时候获取的手机号  后台处理username和mobile 存储  username 存储到mobile中
    class Meta:
        model = UserProfile
        fields = ('username','code','mobile','password')