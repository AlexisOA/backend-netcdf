from django.urls import path
from thredds_api import views

urlpatterns = [
    path('estoc/layers', views.LayersJson.as_view()),
    path('estoc/coords', views.DataThredds.as_view()),
    path('estoc/graphics', views.GraphicThredds.as_view()),
]