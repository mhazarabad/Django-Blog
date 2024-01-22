from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.Landing, name='landing'),
    path('c=<str:category_slug>/', views.Landing, name='landing_category'),
    path('t=<str:tag_slug>/', views.Landing, name='landing_tag'),
    path('<str:post_slug>/', views.PostDetail, name='post_detail'),
]
