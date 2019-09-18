# -*- coding: utf-8 -*-
from tdf.templateuploadcenter import MessageFactory as _
import re
from zope.interface import Invalid, invariant
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from zope import schema
from collective import dexteritytextindexer
from plone.autoform import directives
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone import api
from z3c.form import validator
from tdf.extensionuploadcenter import quote_chars
from plone.uuid.interfaces import IUUID
from Products.validation import V_REQUIRED
from plone.dexterity.browser.view import DefaultView
from zope.security import checkPermission
from plone.indexer.decorator import indexer
from plone.supermodel.directives import primary
from plone.app.textfield import RichText

checkfileextensionimage = re.compile(
    r"^.*\.(png|PNG|gif|GIF|jpg|JPG)").match


def validateImageextension(value):
    if not checkfileextensionimage(value.filename):
        raise Invalid(
            u"You could only add images in the png, gif or jpg file format "
            u"to your project.")
    return True


checkfileextension = re.compile(
    r"^.*\.(ott|OTT|ots|OTS|otp|OTP|otg|OTG)").match


checkdocfileextension = re.compile(
    r"^.*\.(pdf|PDF|odt|ODT)").match

checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match


def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True


def vocabCategories(context):
    # For add forms

    # For other forms edited or displayed
    from tdf.templateuploadcenter.tupcenter import ITUpCenter
    while context is not None and not ITUpCenter.providedBy(context):
        # context = aq_parent(aq_inner(context))
        context = context.__parent__

    category_list = []
    if context is not None and context.available_category:
        category_list = context.available_category

    terms = []
    for value in category_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'),
                                title=value))

    return SimpleVocabulary(terms)


directlyProvides(vocabCategories, IContextSourceBinder)


def vocabAvailLicenses(context):
    """ pick up licenses list from parent """
    from tdf.templateuploadcenter.tupcenter import ITUpCenter
    while context is not None and not ITUpCenter.providedBy(context):
        # context = aq_parent(aq_inner(context))
        context = context.__parent__

    license_list = []
    if context is not None and context.available_licenses:
        license_list = context.available_licenses
    terms = []
    for value in license_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'),
                                title=value))
    return SimpleVocabulary(terms)


directlyProvides(vocabAvailLicenses, IContextSourceBinder)


def vocabAvailVersions(context):
    """ pick up the program versions list from parent """
    from tdf.templateuploadcenter.tupcenter import ITUpCenter
    while context is not None and not ITUpCenter.providedBy(context):
        # context = aq_parent(aq_inner(context))
        context = context.__parent__

    versions_list = []
    if context is not None and context.available_versions:
        versions_list = context.available_versions

    terms = []
    for value in versions_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'),
                                title=value))
    return SimpleVocabulary(terms)


directlyProvides(vocabAvailVersions, IContextSourceBinder)


def isNotEmptyCategory(value):
    if not value:
        raise Invalid(
            u'You have to choose at least one category for your project.')
    return True


def vocabAvailPlatforms(context):
    """ pick up the list of platforms from parent """
    from tdf.templateuploadcenter.tupcenter import ITUpCenter
    while context is not None and not ITUpCenter.providedBy(context):
        # context = aq_parent(aq_inner(context))
        context = context.__parent__

    platforms_list = []
    if context is not None and context.available_platforms:
        platforms_list = context.available_platforms
    terms = []
    for value in platforms_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'),
                                title=value))
    return SimpleVocabulary(terms)


directlyProvides(vocabAvailPlatforms, IContextSourceBinder)


yesnochoice = SimpleVocabulary(
    [SimpleTerm(value=0, title=_(u'No')),
     SimpleTerm(value=1, title=_(u'Yes')), ]
)


@provider(IContextAwareDefaultFactory)
def legal_declaration_title(context):
    return context.title_legaldisclaimer


@provider(IContextAwareDefaultFactory)
def legal_declaration_text(context):
    return context.legal_disclaimer


@provider(IContextAwareDefaultFactory)
def allowedtemplatefileextensions(context):
    return context.allowed_templatefileextension.replace("|", ", ")


@provider(IContextAwareDefaultFactory)
def allowedimagefileextensions(context):
    return context.allowed_imagefileextension.replace("|", ",")


class AcceptLegalDeclaration(Invalid):
    __doc__ = _(u"It is necessary that you accept the Legal Declaration")


def validatetemplatefileextension(value):
    catalog = api.portal.get_tool(name='portal_catalog')
    result = catalog.uniqueValuesFor('allowedtuctemplatefileextensions')
    pattern = r'^.*\.({0})'.format(result[0])
    matches = re.compile(pattern, re.IGNORECASE).match
    if not matches(value.filename):
        raise Invalid(
            u'You could only upload files with an allowed template file '
            u'extension. Please try again with to upload a file with the '
            u'correct template file extension.')
    return True


def validateimagefileextension(value):
    catalog = api.portal.get_tool(name='portal_catalog')
    result = catalog.uniqueValuesFor('allowedtucimagefileextensions')
    pattern = r'^.*\.({0})'.format(result[0])
    matches = re.compile(pattern, re.IGNORECASE).match
    if not matches(value.filename):
        raise Invalid(
            u'You could only upload files with an allowed file extension. '
            u'Please try again to upload a file with the correct file'
            u'extension.')
    return True


class ITUpSmallProject(model.Schema):
    directives.mode(information="display")
    information = schema.Text(
        title=_(u"Information"),
        description=_(
            u"The Dialog to create a new project consists of different "
            u"register. Please go through this register and fill in the "
            u"appropriate data for your project or choose one of the "
            u"options that are provided. You could upload one or more files "
            u"to your project on the register 'File Upload' and "
            u"'Optional Further File Upload'.")
    )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Project Title - minimum 5 and maximum 50 characters"),
        min_length=5,
        max_length=50
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u"Project Summary"),
    )

    dexteritytextindexer.searchable('details')
    primary('details')
    details = RichText(
        title=_(u"Full Project Description"),
        required=False
    )
    model.fieldset('category_compatibility',
                   label=u"Categories / Compatibility",
                   fields=['category_choice', 'compatibility_choice']
                   )

    model.fieldset('legal',
                   label=u"Legal",
                   fields=['licenses_choice', 'title_declaration_legal',
                           'declaration_legal',
                           'accept_legal_declaration']
                   )

    directives.widget(licenses_choice=CheckBoxFieldWidget)
    licenses_choice = schema.List(
        title=_(u'License of the uploaded file'),
        description=_(
            u"Please mark one or more licenses you publish your release."),
        value_type=schema.Choice(source=vocabAvailLicenses),
        required=True,
    )

    directives.mode(title_declaration_legal='display')
    title_declaration_legal = schema.TextLine(
        title=_(u""),
        required=False,
        defaultFactory=legal_declaration_title
    )

    directives.mode(declaration_legal='display')
    declaration_legal = schema.Text(
        title=_(u""),
        required=False,
        defaultFactory=legal_declaration_text
    )

    accept_legal_declaration = schema.Bool(
        title=_(u"Accept the above legal disclaimer"),
        description=_(
            u"Please declare that you accept the above legal disclaimer."),
        required=True
    )

    dexteritytextindexer.searchable('category_choice')
    directives.widget(category_choice=CheckBoxFieldWidget)
    category_choice = schema.List(
        title=_(u"Choose your categories"),
        description=_(
            u"Please select the appropriate categories (one or more) for "
            u"your project."),
        value_type=schema.Choice(source=vocabCategories),
        constraint=isNotEmptyCategory,
        required=True
    )

    contactAddress = schema.TextLine(
        title=_(u"Contact email-address"),
        description=_(u"Contact email-address for the project."),
        constraint=validateEmail
    )

    directives.mode(tucimageextension='display')
    tucimageextension = schema.TextLine(
        title=_(u'The following file extensions are allowed for screenshot '
                u'files (upper case and lower case and mix of both):'),
        defaultFactory=allowedimagefileextensions,
    )

    screenshot = NamedBlobImage(
        title=_(u"Screenshot of the Tempate"),
        description=_(
            u"Add a screenshot by clicking the 'Browse' button. You could "
            u"provide an image of the file format 'png', 'gif' or 'jpg'."),
        required=True,
        constraint=validateimagefileextension
    )

    releasenumber = schema.TextLine(
        title=_(u"Versions Number"),
        description=_(
            u"Version Number of the Template File (up to twelf chars) "
            u"which you upload in this project."),
        default=_(u"1.0"),
        max_length=12,
    )

    directives.widget(compatibility_choice=CheckBoxFieldWidget)
    compatibility_choice = schema.List(
        title=_(u"Compatible with versions of LibreOffice"),
        description=_(
            u"Please mark one or more program versions with which this "
            u"release is compatible with."),
        value_type=schema.Choice(source=vocabAvailVersions),
        required=True,
        default=[]
    )

    directives.mode(tucfileextension='display')
    tucfileextension = schema.TextLine(
        title=_(u'The following file extensions are allowed for template '
                u'files (upper case and lower case and mix of both):'),
        defaultFactory=allowedtemplatefileextensions,
    )

    file = NamedBlobFile(
        title=_(u"The first file you want to upload."),
        description=_(u"Please upload your file."),
        required=True,
        constraint=validatetemplatefileextension,
    )

    directives.widget(platform_choice=CheckBoxFieldWidget)
    platform_choice = schema.List(
        title=_(u"First uploaded file is compatible with the Platform(s)"),
        description=_(
            u"Please mark one or more platforms with which the uploaded file "
            u"is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )

    model.fieldset('fileset1',
                   label=u"File Upload",
                   fields=['filetitlefield', 'platform_choice',
                           'tucfileextension', 'file', ]
                   )

    directives.mode(filetitlefield='display')
    filetitlefield = schema.TextLine(
        title=_(u"The First File You Want To Upload"),
        description=_(
            u"You need only to upload one file to your project. There are "
            u"options for further two file uploads if you want to provide "
            u"files for different platforms.")
    )

    model.fieldset('fileset2',
                   label=u"Optional Further File Upload",
                   fields=['filetitlefield1', 'platform_choice1',
                           'tucfileextension1', 'file1',
                           'filetitlefield2', 'platform_choice2',
                           'tucfileextension2', 'file2']
                   )

    directives.mode(filetitlefield1='display')
    filetitlefield1 = schema.TextLine(
        title=_(u"Second Release File"),
        description=_(
            u"Here you could add an optional second file to your project, if "
            u"the files support different platforms.")
    )

    directives.widget(platform_choice1=CheckBoxFieldWidget)
    platform_choice1 = schema.List(
        title=_(u"Second uploaded file is compatible with the Platform(s)"),
        description=_(
            u"Please mark one or more platforms with which the uploaded file "
            u"is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
    )

    directives.mode(tucfileextension1='display')
    tucfileextension1 = schema.TextLine(
        title=_(u'The following file extensions are allowed for template '
                u'files (upper case and lower case and mix of both):'),
        defaultFactory=allowedtemplatefileextensions,
    )

    file1 = NamedBlobFile(
        title=_(u"The second file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
        constraint=validatetemplatefileextension,
    )

    directives.mode(filetitlefield2='display')
    filetitlefield2 = schema.TextLine(
        title=_(u"Third Release File"),
        description=_(
            u"Here you could add an optional third file to your project, if "
            u"the files support different platforms.")
    )

    directives.widget(platform_choice2=CheckBoxFieldWidget)
    platform_choice2 = schema.List(
        title=_(u"Third uploaded file is compatible with the Platform(s))"),
        description=_(
            u"Please mark one or more platforms with which the uploaded file "
            u"is compatible."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
    )

    directives.mode(tucfileextension2='display')
    tucfileextension2 = schema.TextLine(
        title=_(u'The following file extensions are allowed for template '
                u'files (upper case and lower case and mix of both):'),
        defaultFactory=allowedtemplatefileextensions,
    )

    file2 = NamedBlobFile(
        title=_(u"The third file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
        constraint=validatetemplatefileextension,
    )

    @invariant
    def licensenotchoosen(value):
        if not value.licenses_choice:
            raise Invalid(_(u"Please choose a license for your release."))

    @invariant
    def compatibilitynotchoosen(data):
        if not data.compatibility_choice:
            raise Invalid(_(
                u"Please choose one or more compatible product versions for "
                u"your release."))

    @invariant
    def legaldeclarationaccepted(data):
        if data.accept_legal_declaration is not True:
            raise AcceptLegalDeclaration(
                _(
                    u"Please accept the Legal Declaration about your Release "
                    u"and your Uploaded File"))

    @invariant
    def noOSChosen(data):
        if data.file is not None and data.platform_choice == []:
            raise Invalid(_(
                u"Please choose a compatible platform for the uploaded file."))


@indexer(ITUpSmallProject)
def release_number(context, **kw):
    return context.releasenumber


@indexer(ITUpSmallProject)
def project_compat_versions(context, **kw):
    return context.compatibility_choice


def notifyProjectManager(self, event):
    state = api.content.get_state(self)
    if (self.__parent__.contactForCenter) is not None:
        mailrecipient = str(self.__parent__.contactForCenter)
    else:
        mailrecipient = 'templates@libreoffice.org'
    api.portal.send_email(
        recipient=("{}").format(self.contactAddress),
        sender=(u"{} <{}>").format('Admin of the Website', mailrecipient),
        subject=(u"Your Project {}").format(self.title),
        body=(
            u"The status of your LibreOffice templates project changed. "
            u"The new status is {}").format(
            state)
    )


def notifyAboutNewReviewlistentry(self, event):
    state = api.content.get_state(self)
    if (self.__parent__.contactForCenter) is not None:
        mailrecipient = str(self.__parent__.contactForCenter)
    else:
        mailrecipient = 'templates@libreoffice.org'

    if state == "pending":
        api.portal.send_email(
            recipient=mailrecipient,
            subject=(
                u"A Project with the title {} was added to the review "
                u"list").format(self.title),
            body="Please have a look at the review list and check if the "
                 "project is ready for publication. \n"
                 "\n"
                 "Kind regards,\n"
                 "The Admin of the Website"
        )


def textmodified_project(self, event):
    state = api.content.get_state(self)
    if (self.__parent__.contactForCenter) is not None:
        mailrecipient = str(self.__parent__.contactForCenter)
    else:
        mailrecipient = 'templates@libreoffice.org'
    if state == "published":
        if self.details is not None:
            detailed_description = self.details.output
        else:
            detailed_description = None

        api.portal.send_email(
            recipient=mailrecipient,
            sender=(u"{} <{}>").format('Admin of the Website', mailrecipient),
            subject=(u"The content of the project {} has changed").format(
                self.title),
            body=(
                u"The content of the project {} has changed. Here you get "
                u"the text of the description field of the project: \n"
                u"'{}\n\nand this is the text of the details field:\n"
                u"{}'").format(self.title,
                               self.description,
                               detailed_description),
        )


def notifyAboutNewProject(self, event):
    if (self.__parent__.contactForCenter) is not None:
        mailrecipient = str(self.__parent__.contactForCenter),
    else:
        mailrecipient = 'templates@libreoffice.org'
    api.portal.send_email(
        recipient=mailrecipient,
        subject=(u"A Project with the title {} was added").format(self.title),
        body="A member added a new project"
    )


class ValidateTUpSmallProjectUniqueness(validator.SimpleFieldValidator):
    # Validate site-wide uniqueness of project titles.

    def validate(self, value):
        # Perform the standard validation first
        from tdf.templateuploadcenter.tupproject import ITUpProject

        super(ValidateTUpSmallProjectUniqueness, self).validate(value)
        if value is not None:
            catalog = api.portal.get_tool(name='portal_catalog')
            results1 = catalog({'Title': quote_chars(value),
                                'object_provides':
                                    ITUpProject.__identifier__, })
            results2 = catalog({'Title': quote_chars(value),
                                'object_provides':
                                    ITUpSmallProject.__identifier__, })
            results = results1 + results2

            contextUUID = IUUID(self.context, None)
            for result in results:
                if result.UID != contextUUID:
                    raise Invalid(_(u"The project title is already in use."))


validator.WidgetValidatorDiscriminators(
    ValidateTUpSmallProjectUniqueness,
    field=ITUpSmallProject['title'],
)


class TUpSmallProjectView(DefaultView):
    def canPublishContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def releaseLicense(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        path = "/".join(self.context.getPhysicalPath())
        idx_data = catalog.getIndexDataForUID(path)
        licenses = idx_data.get('releaseLicense')
        return (r for r in licenses)

    def releaseCompatibility(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        path = "/".join(self.context.getPhysicalPath())
        idx_data = catalog.getIndexDataForUID(path)
        compatibility = idx_data.get('getCompatibility')
        return (r for r in compatibility)

    def projectCategory(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        path = "/".join(self.context.getPhysicalPath())
        idx_data = catalog.getIndexDataForUID(path)
        category = idx_data.get('getCategories')
        return (r for r in category)

    def latest_release_date(self):
        return None
