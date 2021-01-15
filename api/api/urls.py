from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing),
    path('fuel-price/india', views.index),
    path('premium/<ott>', views.Services.as_view()),
    path('fuel-price/india/<state>', views.statewise),
    path('movie/search/<plateform>', views.searchMovies),
]
