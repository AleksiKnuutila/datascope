from __future__ import unicode_literals, absolute_import, print_function, division
import six

import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError

from django.db import models
from django.core.exceptions import ValidationError

import jsonfield

from core.models.organisms import Organism


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = jsonfield.JSONField()

    def __getitem__(self, item):
        return self.properties[item]

    @staticmethod
    def validate(data, schema):
        """
        Validates the data against given schema and checks validity of ds_id and ds_spirit.

        :param data: The data to validate
        :param schema: The JSON schema to use for validation.
        :return: Valid data
        """
        if not isinstance(data, dict):
            raise ValidationError(
                "An Individual can only work with a dict as data and got {} instead".format(type(data))
            )
        pk = data.pop("ds_id", None)
        spirit = data.pop("ds_spirit", "")

        try:
            jsonschema.validate(data, schema)
        except SchemaValidationError as exc:
            raise ValidationError(exc)

        if spirit and not isinstance(spirit, six.string_types):
            raise ValidationError("The spirit of an individual needs to be a string not {}.".format(type(spirit)))
        elif spirit:
            data["ds_spirit"] = spirit
        if pk and not isinstance(pk, six.integer_types):
            raise ValidationError("The id of an individual needs to be an integer not {}.".format(type(spirit)))
        elif pk:
            data["ds_id"] = pk

        return data

    def update(self, data, validate=True):
        """
        Update the properties and spirit with new data.

        :param data: The data to use for the update
        :param validate: (optional) whether to validate data or not (yes by default)
        :return: Updated content
        """
        if validate:
            self.validate(data, self.schema)

        spirit = data.pop("ds_spirit", self.spirit)
        self.properties.update(data)
        self.spirit = spirit
        self.save()
        return self.content

    @property
    def content(self):
        """
        Returns the content of this Individual

        :return: Dictionary filled with properties.
        """
        meta = {
            "ds_id": self.id,
            "ds_spirit": self.spirit
        }
        return dict(
            {key: value for key, value in six.iteritems(self.properties) if not key.startswith('_')},
            **meta
        )
