from django.shortcuts import render
from rest_framework import viewsets
from .models import User, Column, Card, Task, Tag, Comment, Notification, Attachment
from .serializers import UserSerializer, ColumnSerializer, CardSerializer, TaskSerializer, TagSerializer, CommentSerializer, NotificationSerializer, AttachmentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    lookup_field = 'id'

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    lookup_field = 'id'
    def perform_create(self, serializer):
        # Define o usuário logado como o criador do comentário
        serializer.save(fk_user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'id'

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def perform_create(self, serializer):
        # Define o usuário logado como o criador do comentário
        serializer.save(fk_user=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = 'id'

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    lookup_field = 'id'

    def perform_create(self, serializer):
        # Define o usuário logado como o criador do anexo
        serializer.save(uploaded_by=self.request.user)