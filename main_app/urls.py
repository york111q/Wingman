from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('mecze/', views.AllMatchesView.as_view(), name="all_matches"),
    path('pools/', views.AllPoolsView.as_view(), name="pool_rank"),
    path('podsumowanie/', views.SummaryView.as_view(), name="summary"),
    path('podsumowanie20/', views.Summary20View.as_view(), name="summary20"),
]
