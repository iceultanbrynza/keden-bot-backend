from django.urls import path
from . import views

urlpatterns = [
    path('register', views.RegisterView, name='register'),
    path('contactid', views.fetchContactId, name='contactId'),
    path('uved', views.UVEDModules, name='uved'),
    path('udl', views.UDLModules, name='udl'),
    path('get_appl/<int:id>', views.return_filled_application_form, name='appl'),
    path('bitrix/notify', views.notify_users_about_progress, name='notify'),
]