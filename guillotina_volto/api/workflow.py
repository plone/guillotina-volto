from guillotina import configure
from guillotina.contrib.workflows.api import WorkflowGET
from guillotina.contrib.workflows.interfaces import IWorkflowBehavior
from guillotina.interfaces import IResource


@configure.service(
    context=IResource,
    method="GET",
    permission="guillotina.AccessContent",
    name="@workflow",
    summary="Workflows for a resource",
    responses={"200": {"description": "Result results on workflows", "schema": {"properties": {}}}},
)
class WorkflowGETVolto(WorkflowGET):
    async def __call__(self):
        workflow = await super().__call__()
        workflow_obj = IWorkflowBehavior(self.context)
        workflow["state"] = {
            "id": workflow_obj.review_state,
            "title": workflow_obj.review_state.capitalize(),
        }
        return workflow
