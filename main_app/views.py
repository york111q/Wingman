from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Matches, Pools
from .forms import HtmlFileForm
from main_app.utils.statistica import stat, stat20
from main_app.utils.new_matches_scrap import scrap_matches, prep_list, update_models


# Create your views here.
class IndexView(TemplateView):
    template_name = 'main_app/index.html'


class AllMatchesView(ListView):
    template_name = 'main_app/matches.html'
    queryset = Matches.objects.order_by('-match_date')


class AllPoolsView(ListView):
    template_name = 'main_app/pools.html'
    queryset = Pools.objects.order_by('-pool_r_rate')

    def get_context_data(self,**kwargs):
        context  = super().get_context_data(**kwargs)
        context['max_pool'] = len(Pools.objects.all())
        return context


class NewMatchesView(TemplateView):
    template_name = 'main_app/new_matches_form.html'


class SummaryView(TemplateView):
    template_name = 'main_app/summary.html'

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
    template_name = 'main_app/summary.html'

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


def new_matches_table_view(request):
    matches_to_do = prep_list()
    if request.method == "POST":
        update_models(request, matches_to_do)
        return redirect(reverse('all_matches'))

    return render(request, 'main_app/new_matches_choice.html', {'matches': matches_to_do})


def new_matches_file_view(request):
    form = HtmlFileForm()

    if request.method == "POST":
        form = HtmlFileForm(request.POST)

        if form.is_valid():
            valid_matches = scrap_matches(request.FILES['file'])
            return redirect(reverse('new_matches2'))

    return render(request, 'main_app/new_matches_form.html', {'form': form})
