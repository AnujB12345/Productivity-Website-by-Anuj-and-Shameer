from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("homepage.urls")),
    path('dashboard/', include("dashboard.urls")),
    path("user/", include("users.urls")),
    path("todo/", include("todo.urls")),
    path("notes/", include("notes.urls")),
    path("calendar/", include("calendar_app.urls")),
    path("timer/", include("timer.urls")),
    path("sw.js", TemplateView.as_view(template_name="sw.js", content_type="application/javascript"), name="service_worker"),
    path('notifications/', include("notifications.urls")), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)