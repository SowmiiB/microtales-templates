from django.contrib import admin
from django.urls import path,include
from tales import views
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('otp-verification/<str:role>/<str:username>/', views.otp_verification, name='otp_verification'),
    path('reader_home/', views.reader_home, name='reader_home'),
    path('writer_home/', views.writer_home, name='writer_home'),
    path('publish/<int:scribeid>', views.publish_page, name='publish_form'),
    path('add_book_to_db/<int:scribeid>', views.add_book_to_db, name='publish'),
    path('content_view/<int:scribeid>', views.content_view, name='content'),
    path('save_for_later/<int:scribeid>', views.save_for_later, name='save_for_later'),
    path('like-scribe/<int:scribe_id>/', views.like_scribe, name='like_scribe'),
    path('fav-author/<int:scribe_id>/', views.add_author_to_fav, name='fav_author'),
    path('view-author/<int:scribe_id>/',views.view_author,name='view_author'),


]