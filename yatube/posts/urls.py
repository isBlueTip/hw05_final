from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    # Group page
    path('group/<slug:pk>/', views.group_list, name='group_list'),
    # User profile
    path('profile/<str:username>/', views.profile, name='profile'),
    # View specific post
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Create new post
    path('create/', views.post_create, name='post_create'),
    # Edit a post
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Comment a post
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
