from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import UserViewSet
from . import views
# from child import views


router = routers.DefaultRouter()
router.register('users',UserViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('healthStatic/<userToken>/',views.healthStaticView,name = 'static-api'),
    path('healthDynamic/<userToken>/',views.healthDynamicView,name = 'dynamic-api'),
	path('model/<str:intercept>/<str:start>/<str:end>/', views.model, name='model'),
	path('query/<str:param>/<str:start>/<str:end>/', views.query, name='query'),
	path('visualize/<str:game>/<str:feature>/', views.visualize, name='visualize')
#     path('child/',
#          views.ChildList.as_view(),
#          name='child-list'),
#     path('child/<int:pk>/',
#          views.ChildDetail.as_view(),
#          name='child-detail'),
#     path('users/',
#          views.UserList.as_view(),
#          name='user-list'),
#     path('users/<int:pk>/',
#          views.UserDetail.as_view(),
#          name='user-detail')
]
