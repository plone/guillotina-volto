from zope.interface import interfaces, Interface, Attribute


class IWorkflowChangedEvent(interfaces.IObjectEvent):
    """An object workflow has been modified"""


class IRegistryChangedEvent(Interface):
    id_ = Attribute("Type id of the registry")
    site = Attribute("Site")
