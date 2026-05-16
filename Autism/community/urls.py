from django.urls import path
from . import views

app_name="community"

urlpatterns=[
    path('community/' , views.community_view, name='community_view'),
    path('create_post/', views.create_post_view, name='create_post_view'),
    path('details_post/<int:post_id>/', views.details_post_view, name='details_post_view'),
    path('like_post/<int:post_id>/', views.like_post_view, name='like_post_view'),
    path('edit_post/<int:post_id>/',views.edit_post_view,name='edit_post_view'),
    path('delete_post/<int:post_id>/',views.delete_post_view,name='delete_post_view'),
    path('edit_comment/<int:comment_id>/',views.edit_comment_view,name='edit_comment_view'),
    path('delete_comment/<int:comment_id>/',views.delete_comment_view,name='delete_comment_view'),


    path('likes/', views.likes_view,name='likes_view'),
    path('like_comment/<int:comment_id>/', views.like_comment_view, name='like_comment_view'),
    path('user/<int:user_id>/posts/', views.user_posts_view, name='user_posts_view'),
    
    ]