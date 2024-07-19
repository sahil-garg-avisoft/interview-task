from rest_framework import serializers
from myapp.models import Item,Movie

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number")
        return value

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value

    def validate(self, data):
        if data.get('name') == data.get('description'):
            raise serializers.ValidationError("Name and description should not be the same")
        return data
    


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

    def validate(self, data):
        title = data.get('title')
        genre = data.get('genre')
        if title and genre and title == genre:
            raise serializers.ValidationError("Title and genre should not be the same")
        return data