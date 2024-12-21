from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tensorflow-api/', include('tensorflow_api.urls')),  # Include TensorFlow API URLs
    path('', TemplateView.as_view(template_name="index.html")),  # Serve React frontend
]
