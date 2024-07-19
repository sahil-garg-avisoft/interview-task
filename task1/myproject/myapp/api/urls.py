from django.urls import path,include
from rest_framework.routers import DefaultRouter
from myapp.api.views import BulkInsertItemsView,MovieViewSet,BulkItemListView

routers = DefaultRouter()
# Register the MovieViewSet with the router
routers.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = [
    path('listitems/',BulkItemListView.as_view(),name='listitems'),
    path('bulkinsert/',BulkInsertItemsView.as_view(),name='bulkinsert'),
    path('',include(routers.urls)),
]