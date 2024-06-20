from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from quotes.forms import AuthorForm, QuoteForm, TagForm
from quotes.models import Author, Quote, Tag


def main(request, page=1):
    quotes_list = Quote.objects.all()
    paginator = Paginator(quotes_list, 10)
    page_number = request.GET.get("page") or page
    page_obj = paginator.get_page(page_number)
    return render(request, "quotes/index.html", {"page_obj": page_obj})


def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, "quotes/author_details.html", context={"author": author})


def tag_detail(request, tag_name, page=1):
    quotes = Quote.objects.filter(tags__name=tag_name).order_by("id")
    tags_per_page = 10
    paginator = Paginator(quotes, tags_per_page)
    page_number = request.GET.get("page") or page
    tags_on_page = paginator.get_page(page_number)
    return render(request, "quotes/tag_details.html", context={"tag": tag_name, "quotes": tags_on_page})


@login_required
def add_tag(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("quotes:root")
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:root")
    else: # GET
        form = TagForm()
    return render(request, "quotes/add_tag.html", {"form": form})


@login_required
def add_author(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("quotes:root")
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:root")
    else:
        form = AuthorForm()
    return render(request, "quotes/add_author.html", {"form": form})


@login_required
def add_quote(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("quotes:root")
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:root")
    else:
        form = QuoteForm()
    return render(request, "quotes/add_quote.html", {"form": form})
