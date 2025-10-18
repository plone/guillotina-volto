from zope.interface import Interface

from guillotina_volto.directives import fieldset_field
from guillotina_volto.fields import RichTextField


class IRichText(Interface):

    fieldset_field("text", "default")
    text = RichTextField(title="RichText field", required=False)
