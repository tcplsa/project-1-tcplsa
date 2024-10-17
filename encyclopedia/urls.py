from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.search, name='search'),
    path('random/', views.random_page, name='random_page'),
    path('new_page/', views.new_page, name='new_page'),
    path('edit/<str:entry>/', views.edit_page, name='edit_page'),
    path('entry/<str:entry>/', views.get_entry, name='get_entry')
]
