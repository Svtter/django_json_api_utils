"""conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
import tests_djapi.views as views

urlpatterns = [
    path('functional_test_json/', views.functional_test_json_view, name='json'),
    path('functional_test_param/', views.functional_test_param_view, name='param'),
    path('functional_test_multipart', views.functional_test_multipart, name='multipart'),
    path('functional_test_other/', views.functional_test_other_view, name='other'),
    path('test_json_client/', views.test_json_client, name='json_client'),
    path('test_json_requester/', views.test_json_requester, name='json_requester')
]
