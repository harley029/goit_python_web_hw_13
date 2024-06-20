import os
import django

from pymongo import MongoClient


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quotes_project.settings") 
django.setup()

from quotes.models import Author, Quote, Tag

client = MongoClient("mongodb://localhost")
db = client.quotes_hw

authors = db.authors.find()
for author in authors:
    Author.objects.get_or_create(
        fullname=author["fullname"],
        born_date=author["born_date"],
        born_location=author["born_location"],
        description=author["description"],
    )

quotes = db.quotes.find()
for quote in quotes:
    tags=[]
    for tag in quote["tags"]:
        tags.append(Tag.objects.get_or_create(name=tag)[0])

    exist_quotes = bool(len(Quote.objects.filter(quote=quote['quote'])))

    if not exist_quotes:
        author = db.authors.find_one({'_id': quote['author']})
        a = Author.objects.get(fullname=author["fullname"])
        q = Quote.objects.create(
            quote=quote["quote"],
            author=a
        )
        for tag in tags:
            q.tags.add(tag)