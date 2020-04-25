# -*- coding: utf-8 -*-
import re

from Products.CMFPlone.utils import safe_unicode
from Products.validation import V_REQUIRED
from tdf.extensionuploadcenter.adapter import IReleasesCompatVersions
from tdf.templateuploadcenter import _

from Acquisition import aq_inner, aq_parent
from plone import api
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.browser.view import DefaultView
from plone.indexer.decorator import indexer
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from plone.supermodel.directives import primary
from z3c.form import validator
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import Invalid, directlyProvides, invariant, provider
from zope.schema.interfaces import (IContextAwareDefaultFactory,
                                    IContextSourceBinder)
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.security import checkPermission


def vocabAvailLicenses(context):
    """ pick up licenses list from parent """

    license_list = getattr(context.__parent__, 'available_licenses', [])
    terms = []
    for value in license_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'),
                                title=value))
    return SimpleVocabulary(terms)


directlyProvides(vocabAvailLicenses, IContextSourceBinder)


def vocabAvailVersions(context):
    """ pick up the program versions list from parent """

    versions_list = getattr(context.__parent__, 'available_versions', [])
    terms = []
    for value in versions_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'),
                                title=value))
    return SimpleVocabulary(terms)


directlyProvides(vocabAvailVersions, IContextSourceBinder)


def vocabAvailPlatforms(context):
    """ pick up the list of platforms from parent """

    platforms_list = getattr(context.__parent__, 'available_platforms', [])
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


@provider(IContextAwareDefaultFactory)
def allowedtemplatefileextensions(context):
    context = context.aq_inner.aq_parent
    return context.allowed_templatefileextension.replace("|", ", ")


def validatetemplatefileextension(value):
    catalog = api.portal.get_tool(name='portal_catalog')
    result = catalog.uniqueValuesFor('allowedtuctemplatefileextensions')
    pattern = r'^.*\.({0})'.format(result[0])
    matches = re.compile(pattern, re.IGNORECASE).match
    if not matches(value.filename):
        raise Invalid(
            u'You could only upload files with an allowed template file '
            u'extension. Please try again to upload a file with the '
            u'correct template file extension.')
    return True


class AcceptLegalDeclaration(Invalid):
    __doc__ = _(safe_unicode(
        "It is necessary that you accept the Legal Declaration"))


class ITUpRelease(model.Schema):
    directives.mode(information="display")
    information = schema.Text(
        title=_(safe_unicode("Information")),
        description=_(safe_unicode(
            "This Dialog to create a new release consists of different "
            "register. Please go through this register and fill in the "
            "appropriate data for your release. This register 'Default' "
            "provide fields for general information of your release. The "
            "next register 'compatibility' is the place to submit "
            "information about the versions with which your release file(s) "
            "is / are compatible. The following register asks for some "
            "legal informations. The next register File Upload' provide a "
            "field to upload your release file. The further register are "
            "optional. There is the opportunity to upload further release "
            "files (for different platforms)."))
    )

    directives.mode(projecttitle='hidden')
    projecttitle = schema.TextLine(
        title=_(safe_unicode("The Computed Project Title")),
        description=_(safe_unicode(
            "The release title will be computed from the parent project "
            "title")),
        defaultFactory=getContainerTitle
    )

    releasenumber = schema.TextLine(
        title=_(safe_unicode("Release Number")),
        description=_(safe_unicode("Release Number (up to twelf chars)")),
        default=_(safe_unicode("1.0")),
        max_length=12
    )

    description = schema.Text(
        title=_(safe_unicode("Release Summary")),
    )

    primary('details')
    details = RichText(
        title=_(safe_unicode("Full Release Description")),
        required=False
    )

    primary('changelog')
    changelog = RichText(
        title=_(safe_unicode("Changelog")),
        description=_(safe_unicode(
            "A detailed log of what has changed since the previous release.")),
        required=False,
    )

    model.fieldset('compatibility',
                   label=safe_unicode("Compatibility"),
                   fields=['compatibility_choice'])

    model.fieldset('legal',
                   label=safe_unicode("Legal"),
                   fields=['licenses_choice', 'title_declaration_legal',
                           'declaration_legal', 'accept_legal_declaration',
                           'source_code_inside', 'link_to_source'])

    directives.widget(licenses_choice=CheckBoxFieldWidget)
    licenses_choice = schema.List(
        title=_(safe_unicode('License of the uploaded file')),
        description=_(safe_unicode(
            "Please mark one or more licenses you publish your release.")),
        value_type=schema.Choice(source=vocabAvailLicenses),
        required=True,
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
            "Please declare that you accept the above legal disclaimer")),
        required=True
    )

    contact_address2 = schema.TextLine(
        title=_(safe_unicode("Contact email-address")),
        description=_(safe_unicode("Contact email-address for the project.")),
        required=False,
        defaultFactory=contactinfoDefault
    )

    source_code_inside = schema.Choice(
        title=_(safe_unicode("Is the source code inside the template?")),
        vocabulary=yesnochoice,
        required=True
    )

    link_to_source = schema.URI(
        title=_(safe_unicode(
            "Please fill in the Link (URL) to the Source Code")),
        required=False
    )

    model.fieldset('fileupload',
                   label=safe_unicode("Fileupload"),
                   fields=['tucfileextension', 'file', 'platform_choice',
                           'information_further_file_uploads'])

    directives.mode(tucfileextension='display')
    tucfileextension = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file = NamedBlobFile(
        title=_(safe_unicode("The first file you want to upload")),
        description=_(safe_unicode("Please upload your file.")),
        required=True,
        constraint=validatetemplatefileextension
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

    directives.mode(information_further_file_uploads='display')
    primary('information_further_file_uploads')
    information_further_file_uploads = RichText(
        title=_(safe_unicode("Further File Uploads for this Release")),
        description=_(safe_unicode(
            "If you want to upload more files for this release, e.g. "
            "because there are files for other operating systems, you'll "
            "find the upload fields on the register 'Further Uploads' and "
            "'Further More Uploads'.")),
        required=False
    )

    model.fieldset('fileset1',
                   label=safe_unicode("Further Uploads"),
                   fields=['tucfileextension1', 'file1', 'platform_choice1',
                           'tucfileextension2', 'file2', 'platform_choice2',
                           'tucfileextension3', 'file3', 'platform_choice3']
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
        constraint=validatetemplatefileextension
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
        constraint=validatetemplatefileextension
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

    directives.mode(tucfileextension3='display')
    tucfileextension3 = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file3 = NamedBlobFile(
        title=_(safe_unicode(
            "The fourth file you want to upload (this is optional)")),
        description=_(safe_unicode("Please upload your file.")),
        required=False,
        constraint=validatetemplatefileextension
    )

    directives.widget(platform_choice3=CheckBoxFieldWidget)
    platform_choice3 = schema.List(
        title=_(safe_unicode(
            "Fourth uploaded file is compatible with the Platform(s)")),
        description=_(safe_unicode(
            "Please mark one or more platforms with which the uploaded file "
            "is compatible.")),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
    )

    model.fieldset('fileset2',
                   label=safe_unicode("Further More Uploads"),
                   fields=['tucfileextension4', 'file4', 'platform_choice4',
                           'tucfileextension5', 'file5', 'platform_choice5']
                   )

    directives.mode(tucfileextension4='display')
    tucfileextension4 = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file4 = NamedBlobFile(
        title=_(safe_unicode(
            "The fifth file you want to upload (this is optional)")),
        description=_(safe_unicode("Please upload your file.")),
        required=False,
        constraint=validatetemplatefileextension
    )

    directives.widget(platform_choice4=CheckBoxFieldWidget)
    platform_choice4 = schema.List(
        title=_(safe_unicode(
            "Fifth uploaded file is compatible with the Platform(s)")),
        description=_(safe_unicode(
            "Please mark one or more platforms with which the uploaded file "
            "is compatible.")),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
    )

    directives.mode(tucfileextension5='display')
    tucfileextension5 = schema.TextLine(
        title=_(safe_unicode(
            'The following file extensions are allowed for template '
            'files (upper case and lower case and mix of both):')),
        defaultFactory=allowedtemplatefileextensions,
    )

    file5 = NamedBlobFile(
        title=_(safe_unicode(
            "The sixth file you want to upload (this is optional)")),
        description=_(safe_unicode("Please upload your file.")),
        required=False,
        constraint=validatetemplatefileextension
    )

    directives.widget(platform_choice5=CheckBoxFieldWidget)
    platform_choice5 = schema.List(
        title=_(safe_unicode(
            "Sixth uploaded file is compatible with the Platform(s)")),
        description=_(safe_unicode(
            "Please mark one or more platforms with which the uploaded file "
            "is compatible.")),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=False,
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
                "your release")))

    @invariant
    def legaldeclarationaccepted(data):
        if data.accept_legal_declaration is not True:
            raise AcceptLegalDeclaration(
                _(safe_unicode(
                    "Please accept the Legal Declaration about "
                    "your Release and your Uploaded File")))

    @invariant
    def testingvalue(data):
        if data.source_code_inside != 1 and data.link_to_source is None:
            raise Invalid(_(safe_unicode(
                "You answered the question, whether the source code is "
                "inside your template with no (default answer). If this is "
                "the correct answer, please fill in the Link (URL) "
                "to the Source Code.")))

    @invariant
    def noOSChosen(data):
        if data.file is not None and data.platform_choice == []:
            raise Invalid(_(safe_unicode(
                "Please choose a compatible platform for the uploaded file.")))


@indexer(ITUpRelease)
def release_number(context, **kw):
    return context.releasenumber


def update_project_releases_compat_versions_on_creation(tuprelease, event):
    IReleasesCompatVersions(
        tuprelease.aq_parent).update(tuprelease.compatibility_choice)


def update_project_releases_compat_versions(tuprelease, event):
    pc = api.portal.get_tool(name='portal_catalog')
    query = '/'.join(tuprelease.aq_parent.getPhysicalPath())
    brains = pc.searchResults({
        'path': {'query': query, 'depth': 1},
        'portal_type': ['tdf.templateuploadcenter.tuprelease',
                        'tdf.templateuploadcenter.tupreleaselink']
    })

    result = []
    for brain in brains:
        if isinstance(brain.compatibility_choice, list):
            result = result + brain.compatibility_choice

    IReleasesCompatVersions(
        tuprelease.aq_parent).set(list(set(result)))


class ValidateTUpReleaseUniqueness(validator.SimpleFieldValidator):
    # Validate site-wide uniqueness of release titles.

    def validate(self, value):
        # Perform the standard validation first
        super(ValidateTUpReleaseUniqueness, self).validate(value)

        if value is not None:
            if ITUpRelease.providedBy(self.context):
                # The release number is the same as the previous value stored
                # in the object
                if self.context.releasenumber == value:
                    return None

            catalog = api.portal.get_tool(name='portal_catalog')
            # Differentiate between possible contexts (on creation or editing)
            # on creation the context is the container
            # on editing the context is already the object
            if ITUpRelease.providedBy(self.context):
                query = '/'.join(self.context.aq_parent.getPhysicalPath())
            else:
                query = '/'.join(self.context.getPhysicalPath())

            result = catalog({
                'path': {'query': query, 'depth': 1},
                'portal_type': ['tdf.templateuploadcenter.tuprelease',
                                'tdf.templateuploadcenter.tupreleaselink'],
                'release_number': value})

            if len(result) > 0:
                raise Invalid(_(safe_unicode(
                    "The release number is already in use. Please choose "
                    "another one.")))


validator.WidgetValidatorDiscriminators(
    ValidateTUpReleaseUniqueness,
    field=ITUpRelease['releasenumber'],
)


class TUpReleaseView(DefaultView):

    def canPublishContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def releaselicense(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        path = "/".join(self.context.getPhysicalPath())
        idx_data = catalog.getIndexDataForUID(path)
        licenses = idx_data.get('releaseLicense')
        return (r for r in licenses)

    def releasecompatibility(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        path = "/".join(self.context.getPhysicalPath())
        idx_data = catalog.getIndexDataForUID(path)
        compatibility = idx_data.get('getCompatibility')
        return (r for r in compatibility)
