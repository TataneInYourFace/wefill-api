from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.permissions.user_permission import IsPostOrIsAuthenticated
from app.serializers import UserSerializer
from app.models import User
from rest_framework_jwt.settings import api_settings
from django.core import serializers

class UserViewSet(viewsets.ViewSet):

    permission_classes = (IsPostOrIsAuthenticated,)
    serializer_class = UserSerializer
    # Router class variables
    lookup_field = 'email'
    lookup_value_regex = '[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,8}'

    def list(self, request):
        """GET - Show all users"""
        # print(request.version)
        users = User.objects.all()
        if users is None:
            return Response({})
        serializer = self.serializer_class(User.objects.all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        """POST - Add new user"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print("xd")
            a = serializer.save()
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            print(a)
            print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
            user = User(serializer.validated_data)
            # user = serializers.deserialize(serializer.validated_data)
            print("aa")
            if isinstance(serializer.data, User):
                print("oui")
            else:
                print("non")
                print("non")
            print(serializer.data)
            print("-----------------")
            print("-----------------")
            print(serializer.validated_data)
            print("eooo")
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            response = serializer.data.copy()
            response.update({'token': token})
            return Response(response, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, email=None):
        """GET - Show <email> user"""
        serializer = self.serializer_class(User.objects.get(email=email))
        return Response(serializer.data)
        # api_result = user_detail.retrieve_the_user(email)
        # return Response(api_result)

    def partial_update(self, request, email=None):
        return Response()

    def destroy(self, request, email=None):
        """DETELE - Delete <email> user"""
        # api_result = user_detail.destroy_the_user(email)
        # return Response(api_result)