from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing),
    path('fuel-price/india', views.index),
    path('premium/search', views.Services.as_view()),
    path('livetv', views.LiveTV),
    path('fuel-price/india/<state>', views.statewise),
    path('hungama/<id>',views.HungamaStreaming.as_view()),
    path('movie/search/<plateform>', views.searchMovies),
    path('zee5/<id>', views.zee5service),
]
