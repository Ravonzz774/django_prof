from django.contrib.auth.hashers import make_password
from django.http import FileResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, UploadFileSerializer, DownloadFileSerializer, \
    DeleteFileSerializer, RenameFileSerializer, AddAccessSerializer, RemoveAccessSerializer, UserFilesSerializer, UserAccessesSerializer
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.views import APIView
from .models import User, File
from rest_framework.authentication import TokenAuthentication
from storage.permissions import IsOwnerPermission, IsAccessPermission
# from .auth import TokenAuthentication
# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            print(token)
            return Response({
                'success': True,
                'message': 'Success',
                'token': token.key
            })
        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'message': 'Success',
                'token': token.key
            })
        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]
    def get(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response({
            'success': True,
            'message': 'Logout'
        })

class FileUpload(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]
    def post(self, request):
        serializer = UploadFileSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save(user=request.user)
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)



class FileView(APIView):
    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAccessPermission()]
        return [IsOwnerPermission()]
    def get(self, request, file_id):
        serializer = DownloadFileSerializer(data={'file_id': file_id})
        if serializer.is_valid():
            response = serializer.save(user=request.user)
            file = response['file']
            filename = response['filename']
            return FileResponse(file, as_attachment=True, filename=filename)

        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


    def delete(self, request, file_id):
        serializer = DeleteFileSerializer(data={'file_id': file_id})
        if serializer.is_valid():
            response = serializer.save(user=request.user)
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def patch(self, request, file_id):
        if request.data.get('name'):
            serializer = RenameFileSerializer(data={'file_id': file_id, 'name': request.data['name']})
        else:
            serializer = RenameFileSerializer(data={'file_id': file_id})

        if serializer.is_valid():
            response = serializer.save(user=request.user)
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AccessView(APIView):
    permission_classes = [IsOwnerPermission,]
    authentication_classes = [TokenAuthentication,]
    def post(self, request, file_id):
        if request.data.get('email'):
            serializer = AddAccessSerializer(data={'file_id': file_id, 'email': request.data['email']})
        else:
            serializer = AddAccessSerializer(data={'file_id': file_id})

        if serializer.is_valid():
            response = serializer.save()
            return Response(response)
        else:
            return Response(serializer.errors, status=status)

    def delete(self, request, file_id):
        if request.data.get('email'):
            serializer = RemoveAccessSerializer(data={'file_id': file_id, 'email': request.data['email']})
        else:
            serializer = RemoveAccessSerializer(data={'file_id': file_id})

        if serializer.is_valid():
            response = serializer.save()
            return Response(response)
        else:
            return Response(serializer.errors, status=status)


class UserFilesView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]
    def get(self, request):
        serializer = UserFilesSerializer(data=request.data)
        if serializer.is_valid():
            response = serializer.save(user=request.user)
            return Response(response)
        else:
            return Response(serializer.errors)


class UserAccessesView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]
    def get(self, request):
        serializer = UserAccessesSerializer(data=request.data)
        if serializer.is_valid():
            response = serializer.save(user=request.user)
            return Response(response)
        else:
            return Response(serializer.errors)