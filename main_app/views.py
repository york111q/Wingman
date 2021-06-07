from django.shortcuts import render
from .models import Matches, Pools
from django.views.generic import TemplateView, ListView
from main_app.utils.statistica import stat, stat20


# Create your views here.
class IndexView(TemplateView):
    template_name = 'main_app/index.html'


class AllMatchesView(ListView):
    template_name = 'main_app/mecze.html'
    queryset = Matches.objects.order_by('-match_date')


class AllPoolsView(ListView):
    template_name = 'main_app/pools.html'
    queryset = Pools.objects.order_by('-pool_r_rate')


class SummaryView(TemplateView):
    template_name = 'main_app/podsumowanie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            all_s, indiv_s = stat()
        except:
            all_s, indiv_s = 0, 0

        context['all_stats_tab'] = all_s
        context['indiv_stats_tab'] = indiv_s
        context['stats20'] = False
        return context


class Summary20View(TemplateView):
    template_name = 'main_app/podsumowanie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            all_s, indiv_s = stat20()
        except:
            all_s, indiv_s = 0, 0

        context['all_stats_tab'] = all_s
        context['indiv_stats_tab'] = indiv_s
        context['stats20'] = True
        return context
