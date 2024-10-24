from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Column, Card, Task, Tag, Comment, Notification, Attachment

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # Campos exibidos na lista de usuários
    list_display = ('login', 'name', 'is_staff', 'is_superuser')
    # Campos de pesquisa na lista de usuários
    search_fields = ('login', 'name')
    # Ordenação de usuários por lista de login em ordem alfabética
    ordering = ('login',)

    # Campos do formulário de edição do usuário
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Campos exibidos no formulário de criação de usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'name', 'password1', 'password2', 'is_staff', 'is_superuser')}
        ),
    )

# Registro do modelo de usuário com a customização
admin.site.register(User, UserAdmin)

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('position',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'fk_column', 'priority', 'fk_user', 'due_date', 'created_at', 'fk_assigned_user')
    list_filter = ('priority', 'fk_column', 'fk_user', 'fk_assigned_user')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('fk_column', 'position')
    autocomplete_fields = ['fk_column', 'fk_user']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'fk_card', 'position', 'completed', 'created_at', 'updated_at')
    list_filter = ('completed',)
    search_fields = ('title', 'fk_card__title')
    ordering = ('fk_card', 'position')
    autocomplete_fields = ['fk_card']

# Admin para o modelo Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


# Admin para o modelo Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_text', 'fk_card', 'fk_user', 'created_at')
    search_fields = ('comment_text', 'fk_card__title', 'fk_user__username')
    autocomplete_fields = ['fk_card', 'fk_user']


# Admin para o modelo Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'fk_user', 'notification_type', 'read', 'created_at')
    list_filter = ('notification_type', 'read')
    search_fields = ('message', 'fk_user__username')
    autocomplete_fields = ['fk_user']


# Admin para o modelo Attachment
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'fk_card', 'uploaded_by', 'created_at')
    search_fields = ('file', 'fk_card__title', 'uploaded_by__username')
    autocomplete_fields = ['fk_card', 'uploaded_by']