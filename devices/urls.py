from django.urls import path
from . import views

app_name = "devices"

urlpatterns = [
    path("", views.DeviceListView.as_view(), name="device_list"),
    path("new/", views.DeviceCreateView.as_view(), name="device_create"),
    path("<int:pk>/edit/", views.DeviceUpdateView.as_view(), name="device_update"),
    path("<int:pk>/delete/", views.DeviceDeleteView.as_view(), name="device_delete"),
]
