from django.db import models

class Item(models.Model):
    id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    release_date = models.DateField()
    genre = models.CharField(max_length=50)
    director = models.CharField(max_length=100)

    def __str__(self):
        return self.title