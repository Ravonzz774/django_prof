import uuid

from rest_framework import serializers, exceptions
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response

from .models import User, File, Access
from .utils import generateFileId

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'min_length': 8, 'write_only': True, 'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, data):
        if User.objects.filter(username=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email is already taken.'})
        return data

    def create(self, validated_data):
        validated_data['username'] = validated_data.pop('email')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


    def create(self, validated_data):
        if User.objects.filter(username=validated_data['email']).exists():
            if User.objects.get(username=validated_data['email']).check_password(validated_data['password']):
                user = User.objects.filter(username=validated_data['email']).first()
                return user

        raise exceptions.AuthenticationFailed({
                'success': False,
                'message': 'Login Failed'
            })


class UploadFileSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField())


    def create(self, validated_data):
        response = []
        user = validated_data.pop('user')

        user_file_names = []
        for userFile in user.files.all():
            user_file_names.append(userFile.filename)

        for file in validated_data['files']:
            file_id = generateFileId()

            if file.name.split('.')[-1] not in ['doc', 'pdf', 'docx', 'zip', 'jpeg', 'jpg', 'png']:
                response.append({
                    "success": False,
                    "message": "File not loaded",
                    'name': file.name,
                })
                continue

            if file.size/1024/1024 > 2:
                response.append({
                    "success": False,
                    "message": "File not loaded",
                    'name': file.name,
                })
                continue


            customname = file.name

            i = 1
            while customname in user_file_names:
                extension = file.name.split('.')[-1]
                basaname = file.name.replace('.' + extension, '')
                customname = f"{basaname} ({i}).{extension}"

                i += 1

            file.name = generateFileId(20)


            uploadFile = File.objects.create(file=file, filename=customname, file_id=file_id)
            access = Access(user=user, file=uploadFile, isOwner=True)
            access.save()


            response.append({
                "success": True,
                "message": "Success",
                'name': customname,
                'url': f"django/files/{file_id}",
                'file_id': file_id,
            })

        return response


class DownloadFileSerializer(serializers.Serializer):
    file_id = serializers.CharField(required=True)

    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if File.objects.filter(file_id=validated_data['file_id']).exists():
            if user.files.filter(file_id=validated_data['file_id']).exists():
                file_field = user.files.filter(file_id=validated_data['file_id']).first()
                file = file_field.file

                return {
                    'file': file,
                    'filename': file_field.filename
                }


            raise exceptions.PermissionDenied()
        raise exceptions.NotFound()


class DeleteFileSerializer(serializers.Serializer):
    file_id = serializers.CharField(required=True)

    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if File.objects.filter(file_id=validated_data['file_id']).exists():
            if user.files.filter(file_id=validated_data['file_id']).exists():
                file = File.objects.filter(file_id=validated_data['file_id']).first()
                accessField = Access.objects.filter(file_id=file.id, user_id=user.id).first()
                if accessField.isOwner:
                    file.delete()
                    accessField.delete()
                    return {
                        "success": True,
                        "message": "File already deleted"
                    }

            raise exceptions.PermissionDenied()
        raise exceptions.NotFound()


class RenameFileSerializer(serializers.Serializer):
    file_id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if File.objects.filter(file_id=validated_data['file_id']).exists():
            if user.files.filter(file_id=validated_data['file_id']).exists():
                file = File.objects.filter(file_id=validated_data['file_id']).first()
                accessField = Access.objects.filter(file_id=file.id, user_id=user.id).first()
                if accessField.isOwner:
                    if not user.files.filter(file_id=file.file_id, filename=validated_data['name']).exists():
                        file.filename = validated_data['name']
                        file.save()
                        return {
                                "success": True,
                                "message": "Renamed"
                            }

                    raise serializers.ValidationError({'name': 'Current file name is already taken'})

            raise exceptions.PermissionDenied()
        raise exceptions.NotFound()


class AddAccessSerializer(serializers.Serializer):
    file_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if File.objects.filter(file_id=validated_data['file_id']).exists():
            if user.files.filter(file_id=validated_data['file_id']).exists():
                file = File.objects.filter(file_id=validated_data['file_id']).first()
                accessField = Access.objects.filter(file_id=file.id, user_id=user.id).first()
                if accessField.isOwner:
                    if User.objects.filter(username=validated_data['email']).exists():
                        addedUser = User.objects.filter(username=validated_data['email']).first()
                        if not Access.objects.filter(file_id=file.id, user_id=addedUser.id).exists():
                            access = Access(user=addedUser, file=file)
                            access.save()

                        response = []
                        accesses = Access.objects.filter(file_id=file.id).all()
                        for ac in accesses:
                            userType = 'co-author'
                            if ac.isOwner:
                                userType = 'author'
                            response.append(
                                {
                                    'full_name': ac.user.get_full_name(),
                                    'email': ac.user.username,
                                    'type': userType,

                                }
                            )

                        return response

                    raise serializers.ValidationError({'email': 'User does not exist'})


            raise exceptions.PermissionDenied()
        raise exceptions.NotFound()




class RemoveAccessSerializer(serializers.Serializer):
    file_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        user = validated_data.pop('user', None)

        if File.objects.filter(file_id=validated_data['file_id']).exists():
            if user.files.filter(file_id=validated_data['file_id']).exists():
                file = File.objects.filter(file_id=validated_data['file_id']).first()
                accessField = Access.objects.filter(file_id=file.id, user_id=user.id).first()
                if accessField.isOwner:
                    if User.objects.filter(username=validated_data['email']).exists():
                        addedUser = User.objects.filter(username=validated_data['email']).first()
                        if Access.objects.filter(file_id=file.id, user_id=addedUser.id).exists():
                            access = Access.objects.filter(file_id=file.id, user_id=addedUser.id).first()
                            if not access.isOwner:
                                access.delete()



                        response = []
                        accesses = Access.objects.filter(file_id=file.id).all()
                        for ac in accesses:
                            userType = 'co-author'
                            if ac.isOwner:
                                userType = 'author'
                            response.append(
                                {
                                    'full_name': ac.user.get_full_name(),
                                    'email': ac.user.username,
                                    'type': userType,
                                }
                            )

                        return response

                    raise serializers.ValidationError({'email': 'User does not exist'})


            raise exceptions.PermissionDenied()
        raise exceptions.NotFound()