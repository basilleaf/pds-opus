import yaml, os
from django.shortcuts import render
from django.http import HttpResponse,Http404
from metrics.views import update_metrics

def guide(request):
    """ renders the API guide at opus/api.index.html
        to edit guide content edit the examples.yaml
        """
    path = os.path.dirname(os.path.abspath(__file__))
    guide_content_file = 'examples.yaml'
    with open(path + "/{}".format(guide_content_file), 'r') as stream:
        try:
            guide = yaml.load(stream)
            return render(request, 'guide.html', locals())

        except yaml.YAMLError as exc:
            print(exc)
