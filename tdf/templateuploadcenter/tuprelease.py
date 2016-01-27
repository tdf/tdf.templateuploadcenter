from tdf.templateuploadcenter import MessageFactory as _
from plone.app.textfield import RichText
from plone.supermodel import model
from zope import schema
from plone.autoform import directives as form
from plone.dexterity.browser.view import DefaultView
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides

from zope.security import checkPermission
from zope.interface import invariant, Invalid
from Acquisition import aq_inner, aq_parent, aq_get, aq_chain
from plone.namedfile.field import NamedBlobFile
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from plone.directives import form
from zope import schema

from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from Products.validation import V_REQUIRED
from z3c.form import validator




def vocabAvailLicenses(context):
    """ pick up licenses list from parent """

    license_list = getattr(context.__parent__, 'available_licenses', [])
    terms = []
    for value in license_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)
directlyProvides(vocabAvailLicenses, IContextSourceBinder)


def vocabAvailVersions(context):
    """ pick up the program versions list from parent """

    versions_list = getattr(context.__parent__, 'available_versions', [])
    terms = []
    for value in versions_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)
directlyProvides(vocabAvailVersions, IContextSourceBinder)


def vocabAvailPlatforms(context):
    """ pick up the list of platforms from parent """

    platforms_list = getattr(context.__parent__, 'available_platforms', [])
    terms = []
    for value in platforms_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)
directlyProvides(vocabAvailPlatforms, IContextSourceBinder)


yesnochoice = SimpleVocabulary(
    [SimpleTerm(value=0, title=_(u'No')),
     SimpleTerm(value=1, title=_(u'Yes')),]
    )



@provider(IContextAwareDefaultFactory)
def getContainerTitle(self):
    return (self.aq_inner.title)


@provider(IContextAwareDefaultFactory)
def contactinfoDefault(context):
    return context.contactAddress


@provider(IContextAwareDefaultFactory)
def legal_declaration_title(context):
    context = context.aq_inner.aq_parent
    return context.title_legaldisclaimer


@provider(IContextAwareDefaultFactory)
def legal_declaration_text(context):
    context = context.aq_inner.aq_parent
    return context.legal_disclaimer


class AcceptLegalDeclaration(Invalid):
    __doc__ = _(u"It is necessary that you accept the Legal Declaration")




class ITUpRelease(model.Schema):

    form.mode(projecttitle='hidden')
    projecttitle = schema.TextLine(
        title=_(u"The Computed Project Title"),
        description=_(u"The project title will be computed from the parent project title"),
        defaultFactory= getContainerTitle
    )


    releasenumber=schema.TextLine(
        title=_(u"Release Number"),
        description=_(u"Release Number (up to eight chars)"),
        default=_(u"1.0"),
        max_length=8
    )


    description = schema.Text(
        title=_(u"Release Summary"),
    )



    form.primary('details')
    details = RichText(
        title=_(u"Full Release Description"),
        required=False
    )



    form.primary('changelog')
    changelog = RichText(
        title=_(u"Changelog"),
        description=_(u"A detailed log of what has changed since the previous release."),
        required=False,
    )


    form.widget(licenses_choice=CheckBoxFieldWidget)
    licenses_choice= schema.List(
        title=_(u'License of the uploaded file'),
        description=_(u"Please mark one or more licenses you publish your release."),
        value_type=schema.Choice(source=vocabAvailLicenses),
        required=True,
    )

    form.widget(compatibility_choice=CheckBoxFieldWidget)
    compatibility_choice= schema.List(
        title=_(u"Compatible with versions of LibreOffice"),
        description=_(u"Please mark one or more program versions with which this release is compatible with."),
        value_type=schema.Choice(source=vocabAvailVersions),
        required=True,
    )



    form.mode(title_declaration_legal='display')
    title_declaration_legal=schema.TextLine(
        title=_(u""),
        required=False,
        defaultFactory = legal_declaration_title
    )


    form.mode(declaration_legal='display')
    declaration_legal = schema.Text(
        title=_(u""),
        required=False,
        defaultFactory = legal_declaration_text

    )

    accept_legal_declaration=schema.Bool(
        title=_(u"Accept the above legal disclaimer"),
        description=_(u"Please declare that you accept the above legal disclaimer"),
        required=True
    )

    contact_address2 = schema.ASCIILine(
        title=_(u"Contact email-address"),
        description=_(u"Contact email-address for the project."),
        required=False,
        defaultFactory = contactinfoDefault
    )

    source_code_inside = schema.Choice(
        title=_(u"Is the source code inside the extension?"),
        vocabulary=yesnochoice,
        required=True
    )

    link_to_source = schema.URI(
        title=_(u"Please fill in the Link (URL) to the Source Code"),
        required=False
    )


    file = NamedBlobFile(
        title=_(u"The first file you want to upload"),
        description=_(u"Please upload your file."),
        required=True,
    )


    form.widget(platform_choice=CheckBoxFieldWidget)
    platform_choice= schema.List(
        title=_(u" First uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or more platforms with which the uploaded file is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    form.mode(information_further_file_uploads='display')
    model.primary('information_further_file_uploads')
    information_further_file_uploads = RichText(
        title = _(u"Further File Uploads for this Release"),
        description = _(u"If you want to upload more files for this release, e.g. because there are files for other operating systems, you'll find the upload fields on the register 'File Upload 1' and 'File Upload 2'."),
        required = False
     )

    form.fieldset('fileset1',
        label=u"File Upload 1",
        fields=['file1', 'platform_choice1', 'file2', 'platform_choice2', 'file3', 'platform_choice3']
    )

    file1 = NamedBlobFile(
        title=_(u"The second file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )


    form.widget(platform_choice1=CheckBoxFieldWidget)
    platform_choice1= schema.List(
        title=_(u"Second uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or more platforms with which the uploaded file is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    file2 = NamedBlobFile(
        title=_(u"The third file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )


    form.widget(platform_choice2=CheckBoxFieldWidget)
    platform_choice2= schema.List(
        title=_(u"Third uploaded file is compatible with the Platform(s))"),
        description=_(u"Please mark one or more platforms with which the uploaded file is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )

    file3 = NamedBlobFile(
        title=_(u"The fourth file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )

    form.widget(platform_choice3=CheckBoxFieldWidget)
    platform_choice3= schema.List(
        title=_(u"Fourth uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or more platforms with which the uploaded file is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    form.fieldset('fileset2',
        label=u"File Upload 2",
        fields=['file4', 'platform_choice4', 'file5', 'platform_choice5']
    )


    file4 = NamedBlobFile(
        title=_(u"The fifth file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )

    form.widget(platform_choice4=CheckBoxFieldWidget)
    platform_choice4= schema.List(
        title=_(u"Fifth uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or more platforms with which the uploaded file is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )

    file5 = NamedBlobFile(
        title=_(u"The sixth file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )

    form.widget(platform_choice5=CheckBoxFieldWidget)
    platform_choice5= schema.List(
        title=_(u"Sixth uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or more platforms with which the uploaded file is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )



    @invariant
    def licensenotchoosen(value):
        if value.licenses_choice == []:
            raise Invalid(_(u"Please choose a license for your release."))

    @invariant
    def compatibilitynotchoosen(data):
        if data.compatibility_choice == []:
            raise Invalid(_(u"Please choose one or more compatible product versions for your release"))

    @invariant
    def legaldeclarationaccepted(data):
        if data.accept_legal_declaration is not True:
           raise AcceptLegalDeclaration(_(u"Please accept the Legal Declaration about your Release and your Uploaded File"))

    @invariant
    def testingvalue(data):
        if data.source_code_inside is not 1 and data.link_to_source is None:
            raise Invalid(_(u"Please fill in the Link (URL) to the Source Code."))

    @invariant
    def noOSChosen(data):
        if data.file is not None and data.platform_choice ==[]:
            raise Invalid(_(u"Please choose a compatible platform for the uploaded file."))






class TUpReleaseView(DefaultView):


     def canPublishContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)