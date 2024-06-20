from django.urls import path

from quotes.views import (
    MainView,
    AuthorDetailView,
    TagDetailView,
    AddTagView,
    AddAuthorView,
    AddQuoteView,
)

app_name = "quotes"

urlpatterns = [
    path("", MainView.as_view(), name="root"),
    path("<int:page>/", MainView.as_view(), name="root_paginate"),
    path("author/<str:author_id>/", AuthorDetailView.as_view(), name="author_detail"),
    path("tag/<str:tag_name>/", TagDetailView.as_view(), name="tag_detail"),
    path(
        "tag/<str:tag_name>/page/<int:page>/",
        TagDetailView.as_view(),
        name="tag_detail_paginate",
    ),
    path("add_author/", AddAuthorView.as_view(), name="add_author"),
    path("add_quote/", AddQuoteView.as_view(), name="add_quote"),
    path("add_tags/", AddTagView.as_view(), name="add_tag"),
]
