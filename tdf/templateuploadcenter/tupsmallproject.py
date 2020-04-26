# -*- coding: utf-8 -*-
from tdf.templateuploadcenter import _
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
from tdf.templateuploadcenter import quote_chars
from plone.uuid.interfaces import IUUID
from Products.validation import V_REQUIRED
from plone.dexterity.browser.view import DefaultView
from zope.security import checkPermission
from plone.indexer.decorator import indexer
from plone.supermodel.directives import primary
from plone.app.textfield import RichText
from Products.CMFPlone.utils import safe_unicode

checkfileextensionimage = re.compile(
    r"^.*\.(png|PNG|gif|GIF|jpg|JPG)").match


def validateImageextension(value):
    if not checkfileextensionimage(value.filename):
        raise Invalid(safe_unicode(
            "You could only add images in the png, gif or jpg file format "
            "to your project."))
    return True


checkfileextension = re.compile(
    r"^.*\.(ott|OTT|ots|OTS|otp|OTP|otg|OTG)").match


checkdocfileextension = re.compile(
    r"^.*\.(pdf|PDF|odt|ODT)").match

checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match


def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(safe_unicode("Invalid email address")))
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
            safe_unicode(
                'You have to choose at least one category for your project.'))
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
    [SimpleTerm(value=0, title=_(safe_unicode('No'))),
     SimpleTerm(value=1, title=_(safe_unicode('Yes'))), ]
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
    __doc__ = _(safe_unicode(
        "It is necessary that you accept the Legal Declaration"))


def validatetemplatefileextension(value):
    catalog = api.portal.get_tool(name='portal_catalog')
    result = catalog.uniqueValuesFor('allowedtuctemplatefileextensions')
    pattern = r'^.*\.({0})'.format(result[0])
    matches = re.compile(pattern, re.IGNORECASE).match
    if not matches(value.filename):
        raise Invalid(safe_unicode(
            'You could only upload files with an allowed template file '
            'extension. Please try again with to upload a file with the '
            'correct template file extension.'))
    return True


def validateimagefileextension(value):
    catalog = api.portal.get_tool(name='portal_catalog')
    result = catalog.uniqueValuesFor('allowedtucimagefileextensions')
    pattern = r'^.*\.({0})'.format(result[0])
    matches = re.compile(pattern, re.IGNORECASE).match
    if not matches(value.filename):
        raise Invalid(safe_unicode(
            'You could only upload files with an allowed file extension. '
            'Please try again to upload a file with the correct file'
            'extension.'))
    return True


class ITUpSmallProject(model.Schema):
    directives.mode(information="display")
    information = schema.Text(
        title=_(safe_unicode("Information")),
        description=_(safe_unicode(
            "The Dialog to create a new project consists of different "
            "register. Please go through this register and fill in the "
            "appropriate data for your project or choose one of the "
            "options that are provided. You could upload one or more files "
            "to your project on the register 'File Upload' and "
            "'Optional Further File Upload'."))
    )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(safe_unicode("Title")),
        description=_(safe_unicode(
            'Project Title - minimum 5 and maximum 50 characters')),
        min_length=5,
        max_length=50
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(safe_unicode("Project Summary")),
    )

    dexteritytextindexer.searchable('details')
    primary('details')
    details = RichText(
        title=_(safe_unicode("Full Project Description")),
        required=False
    )
    model.fieldset('category_compatibility',
                   label=safe_unicode("Categories / Compatibility"),
                   fields=['category_choice', 'compatibility_choice']
                   )

    model.fieldset('legal',
                   label=safe_unicode("Legal"),
                   fields=['licenses_choice', 'title_declaration_legal',
                           'declaration_legal',
                           'accept_legal_declaration']
                   )

    directives.widget(licenses_choice=CheckBoxFieldWidget)
    licenses_choice = schema.List(
        title=_(safe_unicode('License of the uploaded file')),
        description=_(safe_unicode(
            "Please mark one or more licenses you publish your release.")),
        value_type=schema.Choice(source=vocabAvailLicenses),
        required=True,
    )

    directives.mode(title_declaration_legal='display')
    title_declaration_legal = schema.TextLine(
        title=_(safe_unicode("")),
        required=False,
        defaultFactory=legal_declaration_title
    )

    directives.mode(declaration_legal='display')
    declaration_legal = schema.Text(
        title=_(safe_unicode("")),
        required=False,
        defaultFactory=legal_declaration_text
    )

    accept_legal_declaration = schema.Bool(
        title=_(safe_unicode("Accept the above legal disclaimer")),
        description=_(safe_unicode(
            "Please declare that you accept the above legal disclaimer.")),
        required=True
    )

    dexteritytextindexer.searchable('category_choice')
    directives.widget(category_choice=CheckBoxFieldWidget)
    category_choice = schema.List(
        title=_(safe_unicode("Choose your categories")),
        description=_(safe_unicode(
            "Please select the appropriate categories (one or more) for "
            "your project.")),
        value_type=schema.Choice(source=vocabCategories),
        constraint=isNotEmptyCategory,
        required=True
    )

    contactAddress = schema.TextLine(
        title=_(safe_unicode("Contact email-address")),
        description=_(safe_unicode("Contact email-address for the project.")),
        constraint=validateEmail
    )

    directives.mode(tucimageextension='display')
    tucimageextension = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for screenshot '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedimagefileextensions,
    )

    screenshot = NamedBlobImage(
        title=_(safe_unicode("Screenshot of the Tempate")),
        description=_(safe_unicode(
            "Add a screenshot by clicking the 'Browse' button. You could "
            "provide an image of the file format 'png', 'gif' or 'jpg'.")),
        required=True,
        constraint=validateimagefileextension
    )

    releasenumber = schema.TextLine(
        title=_(safe_unicode("Versions Number")),
        description=_(safe_unicode(
            "Version Number of the Template File (up to twelf chars) "
            "which you upload in this project.")),
        default=_(safe_unicode("1.0")),
        max_length=12,
    )

    directives.widget(compatibility_choice=CheckBoxFieldWidget)
    compatibility_choice = schema.List(
        title=_(safe_unicode("Compatible with versions of LibreOffice")),
        description=_(safe_unicode(
            "Please mark one or more program versions with which this "
            "release is compatible with.")),
        value_type=schema.Choice(source=vocabAvailVersions),
        required=True,
        default=[]
    )

    directives.mode(tucfileextension='display')
    tucfileextension = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file = NamedBlobFile(
        title=_(safe_unicode("The first file you want to upload.")),
        description=_(safe_unicode("Please upload your file.")),
        required=True,
        constraint=validatetemplatefileextension,
    )

    directives.widget(platform_choice=CheckBoxFieldWidget)
    platform_choice = schema.List(
        title=_(safe_unicode(
            "First uploaded file is compatible with the Platform(s)")),
        description=_(safe_unicode(
            "Please mark one or more platforms with which the uploaded file "
            "is compatible.")),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )

    model.fieldset('fileset1',
                   label=safe_unicode("File Upload"),
                   fields=['filetitlefield', 'platform_choice',
                           'tucfileextension', 'file', ]
                   )

    directives.mode(filetitlefield='display')
    filetitlefield = schema.TextLine(
        title=_(safe_unicode("The First File You Want To Upload")),
        description=_(safe_unicode(
            "You need only to upload one file to your project. There are "
            "options for further two file uploads if you want to provide "
            "files for different platforms.")),
    )

    model.fieldset('fileset2',
                   label=safe_unicode("Optional Further File Upload"),
                   fields=['filetitlefield1', 'platform_choice1',
                           'tucfileextension1', 'file1',
                           'filetitlefield2', 'platform_choice2',
                           'tucfileextension2', 'file2']
                   )

    directives.mode(filetitlefield1='display')
    filetitlefield1 = schema.TextLine(
        title=_(safe_unicode("Second Release File")),
        description=_(safe_unicode(
            "Here you could add an optional second file to your project, if "
            "the files support different platforms."))
    )

    directives.widget(platform_choice1=CheckBoxFieldWidget)
    platform_choice1 = schema.List(
        title=_(safe_unicode(
            "Second uploaded file is compatible with the Platform(s)")),
        description=_(safe_unicode(
            "Please mark one or more platforms with which the uploaded file "
            "is compatible.")),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
    )

    directives.mode(tucfileextension1='display')
    tucfileextension1 = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file1 = NamedBlobFile(
        title=_(safe_unicode(
            "The second file you want to upload (this is optional)")),
        description=_(safe_unicode("Please upload your file.")),
        required=False,
        constraint=validatetemplatefileextension,
    )

    directives.mode(filetitlefield2='display')
    filetitlefield2 = schema.TextLine(
        title=_(safe_unicode("Third Release File")),
        description=_(safe_unicode(
            "Here you could add an optional third file to your project, if "
            "the files support different platforms.")),
    )

    directives.widget(platform_choice2=CheckBoxFieldWidget)
    platform_choice2 = schema.List(
        title=_(safe_unicode(
            "Third uploaded file is compatible with the Platform(s))")),
        description=_(safe_unicode(
            "Please mark one or more platforms with which the uploaded file "
            "is compatible.")),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
    )

    directives.mode(tucfileextension2='display')
    tucfileextension2 = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file2 = NamedBlobFile(
        title=_(safe_unicode(
            "The third file you want to upload (this is optional)")),
        description=_(safe_unicode("Please upload your file.")),
        required=False,
        constraint=validatetemplatefileextension,
    )

    @invariant
    def licensenotchoosen(value):
        if not value.licenses_choice:
            raise Invalid(_(safe_unicode(
                "Please choose a license for your release.")))

    @invariant
    def compatibilitynotchoosen(data):
        if not data.compatibility_choice:
            raise Invalid(_(safe_unicode(
                "Please choose one or more compatible product versions for "
                "your release.")))

    @invariant
    def legaldeclarationaccepted(data):
        if data.accept_legal_declaration is not True:
            raise AcceptLegalDeclaration(
                _(safe_unicode(
                    "Please accept the Legal Declaration about your Release "
                    "and your Uploaded File")))

    @invariant
    def noOSChosen(data):
        if data.file is not None and data.platform_choice == []:
            raise Invalid(_(safe_unicode(
                "Please choose a compatible platform for the uploaded file.")))


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
        sender=(safe_unicode("{} <{}>")).format('Admin of the Website', mailrecipient),
        subject=(safe_unicode("Your Project {}")).format(self.title),
        body=(safe_unicode(
            "The status of your LibreOffice templates project changed. "
            "The new status is {}")).format(
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
            subject=(safe_unicode(
                "A Project with the title {} was added to the review "
                "list").format(self.title)),
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
            sender=(safe_unicode("{} <{}>")).format('Admin of the Website', mailrecipient),
            subject=(safe_unicode("The content of the project {} has changed")).format(
                self.title),
            body=(safe_unicode(
                "The content of the project {} has changed. Here you get "
                "the text of the description field of the project: \n"
                "'{}\n\nand this is the text of the details field:\n"
                "{}'")).format(self.title,
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
        subject=(safe_unicode("A Project with the title {} was added")).format(self.title),
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
                    raise Invalid(_(safe_unicode("The project title is already in use.")))


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
