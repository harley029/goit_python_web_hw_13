from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from quotes.forms import AuthorForm, QuoteForm, TagForm
from quotes.models import Author, Quote, Tag


class MainView(ListView):
    model = Quote
    template_name = "quotes/index.html"
    context_object_name = "quotes"
    paginate_by = 10

    def get_queryset(self):
        return Quote.objects.all()


class AuthorDetailView(DetailView):
    model = Author
    template_name = "quotes/author_details.html"
    context_object_name = "author"
    pk_url_kwarg = "author_id"


class TagDetailView(View):
    def get(self, request, tag_name, page=1):
        quotes = Quote.objects.filter(tags__name=tag_name).order_by("id")
        paginator = Paginator(quotes, 10)
        page_number = request.GET.get("page") or page
        tags_on_page = paginator.get_page(page_number)
        return render(
            request,
            "quotes/tag_details.html",
            context={"tag": tag_name, "quotes": tags_on_page},
        )


@method_decorator(login_required, name="dispatch")
class AddTagView(View):
    def get(self, request):
        form = TagForm()
        return render(request, "quotes/add_tag.html", {"form": form})

    def post(self, request):
        if "cancel" in request.POST:
            return redirect("quotes:root")
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:root")
        return render(request, "quotes/add_tag.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class AddAuthorView(View):
    def get(self, request):
        form = AuthorForm()
        return render(request, "quotes/add_author.html", {"form": form})

    def post(self, request):
        if "cancel" in request.POST:
            return redirect("quotes:root")
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:root")
        return render(request, "quotes/add_author.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class AddQuoteView(View):
    def get(self, request):
        form = QuoteForm()
        return render(request, "quotes/add_quote.html", {"form": form})

    def post(self, request):
        if "cancel" in request.POST:
            return redirect("quotes:root")
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:root")
        return render(request, "quotes/add_quote.html", {"form": form})
