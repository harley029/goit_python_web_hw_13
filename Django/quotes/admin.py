from django.contrib import admin

from quotes.models import Author, Quote, Tag

# Register your models here.
admin.site.register(Quote)
admin.site.register(Tag)
admin.site.register(Author)
