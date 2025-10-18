from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import interfaces


class IWorkflowChangedEvent(interfaces.IObjectEvent):
    """An object workflow has been modified"""


class IRegistryChangedEvent(Interface):
    id_ = Attribute("Type id of the registry")
    site = Attribute("Site")
