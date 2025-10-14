from guillotina import app_settings
from guillotina import configure


@configure.vocabulary(name="workflow_states")
class WorkflowStateVocabulary:
    def __init__(self, context):
        self.context = context
        workflows_data = app_settings["workflows"]
        workflows_content = app_settings["workflows_content"]
        workflows_names = set()
        self.values = {}
        for value in workflows_content.values():
            workflows_names.add(value)

        for name in workflows_names:
            workflow_content = workflows_data.get(name, None)
            if workflow_content:
                for state_key, state_value in workflow_content["states"].items():
                    self.values[state_key] = state_value["metadata"]["title"]

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
