from django.urls import path
from . import views

urlpatterns = [
    path('register', views.RegisterView, name='register'),
    path('contactid', views.fetchContactId, name='contactId'),
    path('uved', views.UVEDModules, name='uved'),
]