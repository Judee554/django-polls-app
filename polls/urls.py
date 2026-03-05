from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("results_multi/", views.ResultsMultiView.as_view(), name="results_multi"),
    path("multi_vote/", views.MultiVoteView.as_view(), name="multi_vote"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]