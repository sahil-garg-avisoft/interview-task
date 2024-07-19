from rest_framework import generics, status
from rest_framework.response import Response
from myapp.models import Item,Movie
from myapp.api.serializers import ItemSerializer,MovieSerializer
from django.db import DatabaseError, transaction
from rest_framework import viewsets,filters

class BulkItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class BulkInsertItemsView(generics.CreateAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data

        # Determine if the data is a list or a single item
        if isinstance(data, list):
            if not data:
                return Response({'error': 'No items provided in the list'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(data=data, many=True)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        items = [Item(**item_data) for item_data in serializer.validated_data]
                        Item.objects.bulk_create(items, batch_size=1000)  # Adjust batch_size as needed
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                except DatabaseError as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(data, dict):
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        item = Item(**serializer.validated_data)
                        item.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                except DatabaseError as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error': 'Expected a list or a single item'}, status=status.HTTP_400_BAD_REQUEST)

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'genre', 'director']

    # this is how update functionality is using orm in the backend
    
    # def update(self, request, *args, **kwargs):
    #     # Get the object to be updated
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()

    #     # Validate and update the instance using the serializer
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     # Return the updated instance
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    # def perform_update(self, serializer):
    #     # Save the updated instance using the ORM
    #     serializer.save()
