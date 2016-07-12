from django.http import HttpResponse
from django.views.generic import View


class DashboardView(View):
    def get(self, request):
        # view logic here
        return HttpResponse('result')