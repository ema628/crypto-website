from django.urls import path, re_path
from . import views, forms


urlpatterns = [
    path("<str:c>", views.index, name="index"),
    path("<str:id>,<str:c>/<str:time>", views.coins, name="coins"),
    path("compare/<str:id1>/<str:id2>/<str:c>/<str:time>", views.compare, name="compare"),
    path('form/', views.form, name="form"),
    path(r'^coin-autocomplete/$',
        forms.CoinAutocompleteFromList.as_view(),
        name='coin-autocomplete',
    ),
    path('game/hangman/', views.hangman, name="hangman"),
    path('ajax/get_data_hangman/', views.get_data_hangman, name="get_data_hangman"),
    path('game/memory/', views.memory, name="memory"),
    path('favs/show', views.favourites, name="favourites"),
    path('ajax/delete/', views.deleteBookmark, name="deleteBookmark")

]
    
    
    
