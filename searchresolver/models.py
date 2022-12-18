from django.db import models

# Create your models here.

# Create model to store search
# Search contains query, created, responses


class Search(models.Model):
    query = models.TextField()
    response = models.TextField()
    type = models.CharField(max_length=100, default="answer")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.query
