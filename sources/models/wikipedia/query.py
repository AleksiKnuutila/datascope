from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import HttpResource
from core.exceptions import DSInvalidResource, DSHttpError40X


class WikipediaQuery(HttpResource):

    URI_TEMPLATE = 'http://{}.wikipedia.org/w/api.php?{}={}'
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8"
    }
    PARAMETERS = {
        "action": "query",
        "format": "json",
        "redirects": "1",
        "continue": ""
    }
    GET_SCHEMA = {
        "args": {},
        "kwargs": None
    }

    CONFIG_NAMESPACE = "wikipedia"
    WIKI_RESULTS_KEY = "pages"
    WIKI_QUERY_PARAM = "titles"
    ERROR_MESSAGE = "We did not find the page you were looking for. Perhaps you should create it?"

    def send(self, method, *args, **kwargs):
        args = (self.config.wiki_country, self.WIKI_QUERY_PARAM,) + args
        return super(WikipediaQuery, self).send(method, *args, **kwargs)

    def _handle_errors(self):
        """
        Handles missing pages and ambiguity errors
        You can only handle these errors by parsing the body :(
        """
        super(WikipediaQuery, self)._handle_errors()

        # Check general response
        content_type, data = self.content
        if "query" not in data:
            raise DSInvalidResource('Wrongly formatted Wikipedia response, missing "query"', resource=self)
        response = data['query'][self.WIKI_RESULTS_KEY]  # Wiki has response hidden under single keyed dicts :(

        # When searching for pages a dictionary gets returned
        if isinstance(response, dict) and "-1" in response and "missing" in response["-1"]:
            self.status = 404
            raise DSHttpError40X(self.ERROR_MESSAGE, resource=self)
        # When making lists a list is returned
        elif isinstance(response, list) and not response:
            self.status = 404
            raise DSHttpError40X(self.ERROR_MESSAGE, resource=self)

        return response

    @property
    def content(self):
        content_type, data = super(WikipediaQuery, self).content
        if "warnings" in data:
            del(data["warnings"])
        return content_type, data

    def next_parameters(self):
        content_type, data = self.content
        return data.get("continue", {})

    class Meta:
        abstract = True


class WikipediaGenerator(WikipediaQuery):

    def _handle_errors(self):
        """
        Generators have a habit of leaving out the query parameter if the query returns nothing :(
        :return:
        """
        try:
            super(WikipediaGenerator, self)._handle_errors()
        except DSInvalidResource:
            # This indicates the generator didn't find anything under the 'query' key in body
            # In practise it means the searched for title does not exist.
            self.status = 404
            raise DSHttpError40X(self.ERROR_MESSAGE, resource=self)
