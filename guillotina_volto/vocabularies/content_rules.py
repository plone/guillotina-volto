from guillotina import configure

@configure.vocabulary(name="plone.contentrules.events")
class ContentRulesVocabulary:
    def __init__(self, context):
        self.context = context
        self.values = {
            "Comment added": "Comment added",
            "Comment removed": "Comment removed",
            "Comment reply added": "Comment reply added",
            "Comment reply removed": "Comment reply removed",
            "Notify user on comment delete": "Notify user on comment delete",
            "Notify user on comment publication": "Notify user on comment publication",
            "Object added to this container": "Object added to this container",
            "Object copied": "Object copied",
            "Object modified": "Object modified",
            "Object removed from this container": "Object removed from this container",
            "User Created": "User Created",
            "User Logged in": "User Logged in",
            "User Logged out": "User Logged out",
            "User Removed": "User Removed",
            "Workflow state changed": "Workflow state changed",     
        }

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
            return value
        else:
            raise KeyError("No valid state")
