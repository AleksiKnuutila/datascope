from itertools import groupby

from django.shortcuts import render_to_response, RequestContext

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.views.community import HtmlCommunityView
from visual_translations.models import VisualTranslationsCommunity


class VisualTranslationsHtmlView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response):
        data = HtmlCommunityView.data_for(community_class, response)
        if response.status_code == 200:
            lang_key = lambda obj: obj["language"]
            data["results"].sort(key=lang_key)
            response.data["results"] = [(lang, list(words),) for lang, words in groupby(data["results"], lang_key)]
            return response.data
        else:
            return response.data


@api_view()
def info(request):
    """
    Gives information about the available terms and the sizes of the country grids
    """

    terms_info = [
        community.growth_set.filter(type="translations").last().input.individual_set.first()["query"]
        for community in VisualTranslationsCommunity.objects.all()
    ]
    return Response(
        {
            "words": terms_info
        },
        status=status.HTTP_200_OK
    )


def visual_translation_map(request, region, term):
    locales_info = [
        {
            "locale": "{}_{}".format(language, country),
            "image_file": "image-translations/{}/{}_{}.jpg".format(term, language, country),  # TODO: migrate data to visual_translations
            "grid": {
                "width": grid["cell_width"] * grid["columns"],
                "height": grid["cell_height"] * grid["rows"]
            }
        }
        for language, country, grid in VisualTranslationsCommunity.LOCALES
    ]
    context = {
        "region_topo_json": "visual_translations/geo/{}.topo.json".format(region),
        "locales": locales_info,
    }
    return render_to_response("visual_translations/map.html", context, RequestContext(request))
