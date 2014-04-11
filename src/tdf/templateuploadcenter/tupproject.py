from five import grok
from zope import schema
from tdf.templateuploadcenter import _
from plone.directives import form, dexterity
from plone.app.textfield import RichText
from collective import dexteritytextindexer
from zope.schema.interfaces import IContextSourceBinder
import re
from plone.namedfile.field import NamedBlobImage
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import validator
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName




checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match

def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True


@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabCategories(context):
    # For add forms

    # For other forms edited or displayed
    from tdf.templateuploadcenter.tupcenter import ITUpCenter
    while context is not None and not ITUpCenter.providedBy(context):
        #context = aq_parent(aq_inner(context))
        context = context.__parent__

    category_list = []
    if context is not None and context.available_category:
        category_list = context.available_category

    terms = []
    for value in category_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))

    return SimpleVocabulary(terms)




class ITUpProject(form.Schema):


    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Project Title"),
        min_length=5
    )

    description = schema.Text(
        title=_(u"Project Summary"),
    )


    form.primary('details')
    details = RichText(
        title=_(u"Full Project Description"),
        required=False
    )

    dexteritytextindexer.searchable('category_choice')
    category_choice = schema.List(
        title=_(u"Choose your categories"),
        value_type=schema.Choice(source=vocabCategories),
        required=True,
    )


    contactAddress=schema.ASCIILine(
        title=_(u"Contact email-address"),
        description=_(u"Contact email-address for the project."),
        constraint=validateEmail
    )

    homepage=schema.URI(
        title=_(u"Homepage"),
        description=_(u"If the project has an external home page, enter its URL."),
        required=False
    )

    documentation_link=schema.URI(
        title=_(u"URL of documentation repository "),
        description=_(u"If the project has externally hosted documentation, enter its URL."),
        required=False
    )

    project_logo = NamedBlobImage(
        title=_(u"Logo"),
        description=_(u"Add a logo for the project (or organization/company) by clicking the 'Browse' button."),
        required=False,
    )

    screenshot = NamedBlobImage(
        title=_(u"Screemshot of the Template"),
        description=_(u"Add a screenshot by clicking the 'Browse' button."),
        required=False,
    )



class ValidateTUpProjectUniqueness(validator.SimpleFieldValidator):
    """Validate site-wide uniquneess of project titles.
    """

    def validate(self, value):
        # Perform the standard validation first
        super(ValidateTUpProjectUniqueness, self).validate(value)

        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog({'title': value,
                               'object_provides': ITUpProject.__identifier__})

            contextUUID = IUUID(self.context, None)
            for result in results:
                if result.UID != contextUUID:
                    raise Invalid(_(u"The project title is already in use"))

validator.WidgetValidatorDiscriminators(
    ValidateTUpProjectUniqueness,
    field=ITUpProject['title'],
)
grok.global_adapter(ValidateTUpProjectUniqueness)



# View

class View(dexterity.DisplayForm):
    grok.context(ITUpProject)
    grok.require('zope2.View')
