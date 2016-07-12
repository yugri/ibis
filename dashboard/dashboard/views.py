from django.shortcuts import render
from django.views.generic import View
from collector.tasks import mul, run_bing_spider, run_test_spider

from dashboard.forms import CrawlerForm
from django.contrib import messages


class IndexView(View):
    form_class = CrawlerForm
    initial = {'key': 'value'}
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            query = form.cleaned_data['keywords_phrase']

            task = run_bing_spider.delay(query)
            # task = run_contacts_spider.delay(query)
            # task = mul.delay(3, 1000) # FOR TESTING ONLY
            # run_test_spider() # FOR TESTING ONLY
            messages.add_message(request, messages.INFO, 'Okay! Your crawler now in job!')

        return render(request, self.template_name, {'form': form})