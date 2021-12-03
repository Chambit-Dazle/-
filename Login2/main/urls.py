#main 서브앱의 urls


from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Login.as_view(), name="login"),
    path('select/', views.setResult, name = 'setResult' )
]
