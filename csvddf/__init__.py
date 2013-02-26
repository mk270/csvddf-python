
#  csvddf, a basic web library for CSV dialect descriptions, by Martin Keegan
#
#  Copyright (C) 2013  Martin Keegan
#
#  This programme is free software; you may redistribute and/or modify
#  it under the terms of the Apache Software Licence v2.0

import json
import csv

class ConfigurationError(Exception): pass
class ParseError(Exception): pass

class CSVDDF(object):
    """
    A class for generating and reading CSVDDF files
    """
    fields = [
        "delimiter",
        "doublequote",
        "lineterminator",
        "quotechar",
        "skipinitialspace"
        ]
    format_version = 1.0

    def __init__(self, **kwargs):
        """
        Arguments:

        dialect: a csv.Dialect object
        json: a string containing a CSVDDF dictionary
        

        """
        config_sources = ["dialect", "json"]
        arguments = filter(lambda arg: arg in config_sources, kwargs.keys())
        if len(arguments) == 0:
            raise ConfigurationError("""Either `dialect' or `json' argument must be specified.""")
        if len(arguments) > 1:
            raise ConfigurationError("""Only one of `dialect' or `json' argument may be specified.""")

        if "dialect" in kwargs:
            self._init_from_dialect(kwargs["dialect"])
        elif "json" in kwargs:
            self._init_from_json(kwargs["json"])
    
    def _init_from_dialect(self, dialect):
        [ setattr(self, f, getattr(dialect, f)) for f in self.fields ]

    def _init_from_json(self, json_data):
        try:
            j = json.loads(json_data)
        except:
            raise ParseError("Could not unmarshall JSON; file malformed?")

        top_level_keys = ["csvddf_version", "dialect"]
        if sorted(j.keys()) != sorted(top_level_keys):
            for k in top_level_keys:
                if k not in j:
                    raise ParseError("Could not find `%s' key in JSON file" % k)
            for k in j.keys():
                if k not in top_level_keys:
                    raise ParseError("Found extraneous key `%s' in JSON file" % k)

        try:
            dialect = j["dialect"]
            if sorted(dialect.keys()) != sorted(self.fields):
                for k in self.fields:
                    if k not in dialect:
                        raise ParseError("Could not find `%s' key in JSON file" % k)
                for k in dialect.keys():
                    if k not in self.fields:
                        raise ParseError("Found extraneous key `%s' in JSON file" % k)

            for k, v in dialect.iteritems():
                setattr(self, k, v)
        except:
            raise ParseError

    def _dialect(self):
        return dict([ (k, getattr(self, k)) for k in self.fields ])

    def as_dict(self):
        return {
            "csvddf_version": self.format_version,
            "dialect": self._dialect()
            }

    def as_json(self):
        return json.dumps(self.as_dict(), indent=2)

    def as_dialect(self):
        class Dialect(csv.Dialect):
            _name = "from_csvddf"
            quoting = csv.QUOTE_MINIMAL

        dialect = self._dialect()
        [ setattr(Dialect, k, str(v)) for k, v in dialect.iteritems() ]
        
        return Dialect()
