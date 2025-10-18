from guillotina import configure

from guillotina_volto.api.types import Types


@configure.vocabulary(name="content_types")
class ContentTypesVocabulary:
    def __init__(self, context):
        self.context = context
        types_data = Types.get_local_types(self.context)
        self.values = {}
        for item_type in types_data:
            self.values[item_type["title"]] = item_type["title"]

    def keys(self):
        return self.values

    def __iter__(self):
        return iter([x for x in self.values])

    def __contains__(self, value):
        return value in self.values

    def __len__(self):
        return len(self.values)

    def getTerm(self, value):
        if value in self.values:
            return self.values[value]
        else:
            raise KeyError("No valid state")
