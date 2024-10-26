from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from kanban.views import UserViewSet, ColumnViewSet, CardViewSet, TaskViewSet, TagViewSet, CommentViewSet, NotificationViewSet, AttachmentViewSet, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Kanban",
        default_version='v1',
        description="Documentação da API para o projeto Kanban",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="suporte@kanban.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

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
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
