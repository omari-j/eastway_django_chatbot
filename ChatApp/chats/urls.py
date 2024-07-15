from django.urls import path
from . import views

urlpatterns = [
    path('<id>', views.load_chat, name='load_chat'),
    path('delete/<id>', views.delete_chat, name='delete_chat')
]
