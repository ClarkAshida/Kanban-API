from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Gerenciador de usuário personalizado
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
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')

        return self.create_user(login, name, password, **extra_fields)

# Modelo de usuário personalizado
class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='kanban_users_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='kanban_users_permissions',
        blank=True
    )

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.login

# Modelo de coluna (Kanban)
class Column(models.Model):
    name = models.CharField(max_length=100)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='columns')

    def __str__(self):
        return self.name

# Modelo de cartão (Kanban)
class Card(models.Model):
    PRIORITY_CHOICES = (
        ('U', 'Urgente'),
        ('I', 'Importante'),
        ('M', 'Média'),
        ('B', 'Baixa'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    fk_column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='cards')
    position = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards')
    fk_assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_cards', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Modelo de tarefa (para cartões)
class Task(models.Model):
    title = models.CharField(max_length=100)
    position = models.IntegerField()
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='tasks')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Modelo de tag (para cartões)
class Tag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=7,
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Cor hexadecimal inválida')]
    )
    cards = models.ManyToManyField(Card, related_name='tags')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Modelo de comentário (para cartões)
class Comment(models.Model):
    comment_text = models.TextField(blank=True, null=True)
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments')
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text

# Modelo de notificação
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

# Modelo de anexo (para cartões)
class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name