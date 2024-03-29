from django.urls import path
from thredds_api import views

urlpatterns = [
    path('estoc/fixedobslayers', views.FixedObsLayers.as_view()),
    path('estoc/gliderslayers', views.GlidersLayers.as_view()),
    path('estoc/coords', views.DataThredds.as_view()),
    path('estoc/coordsprofiles', views.DataThreddsProfiles.as_view()),
    path('estoc/formdata', views.DataForm.as_view()),
    path('estoc/formdataProfiles', views.DataFormProfiles.as_view()),
    path('estoc/convertcsv', views.CSVFile.as_view()),
    path('estoc/threddscatalog', views.CatalogThredds.as_view()),
    path('gliders/dataset', views.GlidersDataset.as_view()),
    path('gliders/datasetvariable', views.GlidersDatasetVariable.as_view()),
]