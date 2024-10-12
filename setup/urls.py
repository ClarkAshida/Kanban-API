from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from kanban.views import UserViewSet, ColumnViewSet, CardViewSet, TaskViewSet, TagViewSet, CommentViewSet, NotificationViewSet, AttachmentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'columns', ColumnViewSet)
router.register(r'cards', CardViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'attachments', AttachmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
