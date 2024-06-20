from django import forms
from quotes.models import Tag, Author, Quote


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["fullname", "born_date", "born_location", "description"]

    def clean_fullname(self):
        fullname = self.cleaned_data.get("fullname")
        if Author.objects.filter(fullname=fullname).exists():
            raise forms.ValidationError("This author is already exists.")
        return fullname


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["quote", "author", "tags"]

    def clean(self):
        cleaned_data = super().clean()
        quote = cleaned_data.get("quote")
        author = cleaned_data.get("author")

        if quote and author:
            # Перевірка унікальності цитати для конкретного автора
            if Quote.objects.filter(quote=quote, author=author).exists():
                raise forms.ValidationError("This quote by the author already exists.")
        return cleaned_data
