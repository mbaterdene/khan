
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('ckeditor', include('ckeditor_uploader.urls')),
    path('blog/', include('blog.urls')),
    path('comment/', include('comment.urls')),
    path('likes/', include('likes.urls')),
    path('my_notifications/', include('my_notifications.urls')),
    path('user/', include('user.urls')),
    path('', include('webpages.urls')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('search/', views.search, name="search"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
