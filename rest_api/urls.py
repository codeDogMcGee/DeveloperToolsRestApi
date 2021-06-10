from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('organizations/', views.OrganizationsView.as_view(), name='organizations'),
    path('organizations/<str:sort_column>/<int:ascending>/', views.OrganizationsSortedView.as_view(), name='organizations-sorted'),
    path('organizations/csv/', views.OrganizationsCsvDownloadView.as_view(), name='organizations-csv'),
    path('organizations/<str:sort_column>/<int:ascending>/csv/', views.OrganizationsSortedCsvView.as_view(), name='organizations-sorted-csv'),
]