from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Q
from .models import User, Board, Column, Card, Task, Tag, Comment, Notification, Attachment, BoardCollaborator
from .serializers import UserSerializer, BoardSerializer, ColumnSerializer, CardSerializer, TaskSerializer, TagSerializer, CommentSerializer, NotificationSerializer, AttachmentSerializer, BoardCollaboratorSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.authentication import BasicAuthentication


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    authentication_classes = [BasicAuthentication] # Adiciona autenticação básica
    #authentication_classes = [JWTAuthentication] # Adiciona autenticação JWT
    permission_classes = [IsAuthenticated] # Adiciona permissão de autenticação

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Retorna apenas os quadros que o usuário possui ou tem permissão
        return Board.objects.filter(
            Q(fk_user=user) |
            Q(collaborators__fk_user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(fk_user=self.request.user)

    def perform_update(self, serializer):
        board = self.get_object()
        if not board.has_permission(self.request.user, permission_type='edit'):
            raise PermissionDenied("Você não tem permissão para editar este quadro.")
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.has_permission(self.request.user, permission_type='admin'):
            raise PermissionDenied("Você não tem permissão para deletar este quadro.")
        instance.delete()


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Retorna apenas as colunas de quadros que o usuário possui ou tem permissão
        return Column.objects.filter(
            fk_board__fk_user=user
        ) | Column.objects.filter(
            fk_board__collaborators__fk_user=user
        )

    def perform_create(self, serializer):
        fk_board = serializer.validated_data.get('fk_board')
        if not fk_board.has_permission(self.request.user, permission_type='edit'):
            raise PermissionDenied("Você não tem permissão para adicionar colunas a este quadro.")
        serializer.save(fk_user=self.request.user)

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    lookup_field = 'id'

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

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = 'id'

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    lookup_field = 'id'

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class BoardCollaboratorViewSet(viewsets.ModelViewSet):
    queryset = BoardCollaborator.objects.all()
    serializer_class = BoardCollaboratorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Se o usuário for admin do sistema, ele pode visualizar todos os colaboradores
        if user.is_staff:
            return BoardCollaborator.objects.all()

        # Para outros usuários, filtrar colaboradores apenas dos boards onde eles têm permissão
        board_id = self.request.query_params.get('board_id')

        # Se nenhum board_id foi fornecido, retornar apenas os colaboradores onde o usuário tem permissão
        if not board_id:
            return BoardCollaborator.objects.filter(
                fk_board__fk_user=user  # Dono do quadro
            ) | BoardCollaborator.objects.filter(
                fk_user=user  # Colaborador
            )

        # Se o board_id foi fornecido, verificar se o usuário tem permissão de visualização
        board = Board.objects.filter(id=board_id).first()
        if not board:
            raise PermissionDenied("O quadro especificado não existe.")

        if not board.has_permission(user, permission_type='view'):
            raise PermissionDenied("Você não tem permissão para acessar este quadro.")

        return BoardCollaborator.objects.filter(fk_board=board)

    def perform_create(self, serializer):
        # Permissão de administrador do quadro é necessária para adicionar colaboradores
        board_id = self.request.data.get('fk_board')
        board = Board.objects.filter(id=board_id).first()

        if not board or not board.has_permission(self.request.user, permission_type='admin'):
            raise PermissionDenied("Você não tem permissão para adicionar colaboradores a este quadro.")

        serializer.save()

    def perform_destroy(self, instance):
        # Permissão de administrador do quadro é necessária para remover colaboradores
        board = instance.fk_board
        if not board.has_permission(self.request.user, permission_type='admin'):
            raise PermissionDenied("Você não tem permissão para remover colaboradores deste quadro.")

        instance.delete()
