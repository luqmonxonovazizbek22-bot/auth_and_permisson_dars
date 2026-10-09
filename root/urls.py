from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView




schema_view = get_schema_view(
    openapi.Info(
        title="Student API",
        default_version='v1',
        description="Student CRUD API hujjati",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # path('api/token/', obtain_auth_token),
    # path('api/token/', TokenObtainPairView.as_view()),
    # path('api/token/refresh/', TokenRefreshView.as_view()),
    # path('api/token/verify/', TokenVerifyView.as_view()),

    path("register/", RegisterAPIView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('logout/', LogoutGenericAPIView.as_view()),
    path('verify/', VerifyEmailView.as_view()),
    path('forgot-password/', ForgotPasswordAPIView.as_view()),

    path("forgot-password/",ForgotPasswordAPIView.as_view(),name="forgot-password"
    ),

    path("reset-password/",ResetPasswordAPIView.as_view(),name="reset-password"
    ),
]
