from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blogapp import views

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blogapp.urls")),


    # PASSWORD MANAGEMENT
    path(
        "accounts/password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="password_change.html",
            success_url="/profile/"
        ),
        name="password_change",
    ),
    path('ckeditor/', include('ckeditor_uploader.urls'))

]
