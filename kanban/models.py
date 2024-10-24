from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

#BaseUserManager é uma classe do Django que fornece métodos para criar usuários e superusuários
class UserManager(BaseUserManager):
    def create_user(self, login, name, password, **extra_fields):
        if not login:
            raise ValueError('O campo Login deve ser preenchido')
        if not name:
            raise ValueError('O campo Nome deve ser preenchido')
        if not password:
            raise ValueError('O campo Senha deve ser preenchido')

        user = self.model(login=login, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')

        return self.create_user(login, name, password, **extra_fields)

#AbstractBaseUser é uma classe do Django que fornece a implementação de um modelo de usuário customizado
class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='kanban_users_groups',  # Alterado para evitar conflito
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='kanban_users_permissions',  # Alterado para evitar conflito
        blank=True
    )

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.login

#Modelo das colunas do quadro Kanban, possui nome e posição
class Column(models.Model):
    name = models.CharField(max_length=100)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#Modelo dos cartões do quadro Kanban, possui título, descrição, posição, data de início, data de término, prioridade, categoria, usuário e usuário atribuído
class Card(models.Model):
    PRIORITY_CHOICES = (
        ('U', 'Urgente'),
        ('I', 'Importante'),
        ('M', 'Média'),
        ('B', 'Baixa'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    fk_column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='cards') #FK Column
    position = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M', null=False, blank=False)
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards') #FK User
    fk_assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_cards', null=True, blank=True) #FK User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

#Modelo das tarefas dos cartões, possui título, posição, cartão e status de conclusão
class Task(models.Model):
    title = models.CharField(max_length=100)
    position = models.IntegerField()
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='tasks') #FK Card
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

#Modelo das tags, possui nome, cor e cartões
class Tag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=7,
        #Validação de cor hexadecimal
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Invalid hex color')]
    )
    cards = models.ManyToManyField(Card, related_name='tags') #M2M Cards
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#Modelo dos comentários, possui texto, cartão e usuário
class Comment(models.Model):
    comment_text = models.TextField(blank=True, null=True)
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments') #FK Card
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text

#Modelo das notificações, possui mensagem, usuário, tipo e status de leitura
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('comment', 'Comentário'),
        ('task_completed', 'Tarefa Concluída'),
        ('card_moved', 'Cartão Movido'),
    )
      
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='comment')
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

#Modelo dos anexos, possui arquivo, cartão e usuário
class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name