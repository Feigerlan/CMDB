from django.conf.urls import include, url
from django.contrib import admin
from .views import *
urlpatterns = [
    url(r'index/',index),
    url(r'login/',login),
    url(r'logout/', logout),
    url(r'^register/',register),

    url(r'DeviceAdd/',DeviceAdd),
    url(r'DeviceList',DeviceList),
    url(r'DeviceAll', DeviceAll),
    url(r'DelDevice', DelDevice),
    url(r'DevicesAdd', DevicesAdd),
    url(r'DeviceSearch', DeviceSearch),
    url(r'DeviceEdit', DeviceEdit),
    url(r'GetDevice/', GetDevice),
    url(r'^GetDeviceLog/$', GetDeviceLog),


    url(r'CabinetAdd',CabinetAdd),
    url(r'CabinetsAdd', CabinetsAdd),
    url(r'CabinetList',CabinetList),
    url(r'CabinetAll', CabinetAll),
    url(r'DelCabinet', DelCabinet),


    url(r'DataroomAdd', DataroomAdd),
    url(r'DataroomList', DataroomList),
    url(r'DelDataroom', DelDataroom),

    url(r'^OperLog/$',OperLog),

    url(r'output/', output),
    url(r'^outputCabinets/', outputCabinets),

    url(r'dataroomselect',dataroomselect),
    url(r'cabinetselect(\d+)', cabinetselect),

    url(r'UserList', UserList),
    url(r'UserGroup', GroupList),
    url(r'UserEdit', UserEdit),


]