from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView
from wiki_news.models import WikiNewsCommunity


urlpatterns = [
    url(r'^wiki-algo-news/$', CommunityView.as_view(), {"community_class": WikiNewsCommunity})
]