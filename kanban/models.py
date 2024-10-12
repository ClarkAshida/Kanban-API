from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin

class UserManager(UserManager):
    def create_user(self, email, username, cpf, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo Email deve ser preenchido')
        if not cpf:
            raise ValueError('O campo CPF deve ser preenchido')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, cpf=cpf, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, cpf, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')

        return self.create_user(email, username, cpf, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    cpf = models.CharField(
        max_length=11, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{11}$', message='CPF deve conter 11 dígitos numéricos')]
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True, unique=True)

    # Evitar conflitos de reverse accessors
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='kanban_users',  # Define um related_name único
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='kanban_users_permissions',  # Define um related_name único
        blank=True,
        help_text='Specific permissions for this user.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'cpf']

    objects = UserManager()

    def __str__(self):
        return self.email

class Column(models.Model):
    name = models.CharField(max_length=100)
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Card(models.Model):
    PRIORITY_CHOICES = (
        ('U', 'Urgente'),
        ('I', 'Importante'),
        ('M', 'Média'),
        ('B', 'Baixa'),
    )
    CATEGORY_CHOICES = (
        ('B', 'Backlog'),
        ('P', 'Em Progresso'),
        ('S', 'Standby'),
        ('D', 'Desenvolvida'),
        ('T', 'Testando'),
        ('F', 'Finalizada'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    fk_column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='cards') #FK Column
    position = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M', null=False, blank=False)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='B', null=False, blank=False)
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards') #FK User
    fk_assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_cards', null=True, blank=True) #FK User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

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

class Comment(models.Model):
    comment_text = models.TextField(blank=True, null=True)
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments') #FK Card
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text

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

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    fk_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name