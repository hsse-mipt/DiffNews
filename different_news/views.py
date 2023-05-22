from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from .forms import QueryForm
from .utils import get_certain_news

from pandas import DataFrame


class IndexView(generic.ListView):
    form_class = QueryForm
    initial = {}
    template_name = "index.html"
    context_object_name = "latest_analyzed_news"
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        self.context['form'] = form
        return render(request, self.template_name, context=self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.context['form'] = form

        if form.is_valid():
            event = form.cleaned_data['event']
            entity = form.cleaned_data['entity']

            df = get_certain_news(event.split())

            titles = df['title']
            news = df['description']
            links = df['link']
            published = df['published']

            data = DataFrame({
                'title': titles,
                'description': news,
                'link': links,
                'pub_date': published
            })

            data = data.head(3)

            return HttpResponse(data.to_json(force_ascii=False))
            # with open('analyzed_news.json', 'w', encoding='utf-8-sig') as js_file:
            #     data.to_json(js_file, force_ascii=False)
        else:
            return HttpResponse('Invalid data')

        return render(request, self.template_name, context=self.context)