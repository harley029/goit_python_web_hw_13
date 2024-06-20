from django.db import models

from core.models import BaseModel


class Author(BaseModel):
    fullname = models.CharField(max_length=50)
    born_date = models.CharField(max_length=50)
    born_location = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return f"{self.fullname}"


class Tag(BaseModel):
    name = models.CharField(max_length=30, null = True, unique=True)

    def __str__(self):
        return f"{self.name}"


class Quote(BaseModel):
    quote = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=None, null=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f"{self.quote}"
