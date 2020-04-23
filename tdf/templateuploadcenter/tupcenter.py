# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.multilingual.dx import directives
from plone.app.textfield import RichText
from plone.supermodel import model
from Products.CMFPlone.browser.search import quote_chars
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.ZCTextIndex.ParseTree import ParseError
from tdf.templateuploadcenter import _
from tdf.templateuploadcenter.tupproject import ITUpProject
from zope import schema
import re
from zope.interface import Invalid
from plone.supermodel.directives import primary

MULTISPACE = u'\u3000'.encode('utf-8')
BAD_CHARS = ('?', '-', '+', '*', MULTISPACE)

checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match


def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True


class ITUpCenter(model.Schema):
    """ An Template Upload Center for LibreOffice templates.
    """

    title = schema.TextLine(
        title=_(safe_unicode("Name of the Template Center")),
    )

    description = schema.Text(
        title=_(safe_unicode('Descirption Of The Template Center')),
    )

    product_description = schema.Text(
        title=_(safe_unicode("Description Of The Features Of Templates"))
    )

    product_title = schema.TextLine(
        title=_(safe_unicode("Template Product Name")),
        description=_(safe_unicode
                      ("Name of the Template product, e.g. only Templates "
                       "or LibreOffice Templates")),
    )

    model.fieldset('categories_et_all',
                   label=safe_unicode("Categories et all"),
                   fields=['available_category', 'available_licenses',
                           'available_versions', 'available_platforms'])

    available_category = schema.List(title=_(safe_unicode("Available Categories")),
                                     default=['Accounting',
                                              'Agenda',
                                              'Arts',
                                              'Book',
                                              'Brochure / Pamphlet',
                                              'Budget',
                                              'Business',
                                              'Business POS',
                                              'Business Shipping',
                                              'Calendar',
                                              'Cards',
                                              'Curriculum Vitae',
                                              'CD / DVD|CD',
                                              'Certificate',
                                              'Checkbook',
                                              'Christmas',
                                              'Computer',
                                              'Conference',
                                              'E-book',
                                              'Education',
                                              'Academia',
                                              'Elementary/Secondary '
                                              'school panels',
                                              'Envelope'
                                              'Fax',
                                              'Genealogy',
                                              'Grocery',
                                              'Invoice',
                                              'Labels',
                                              'LibreLogo',
                                              'Letter',
                                              'Magazine',
                                              'Media',
                                              'Medical',
                                              'Memo',
                                              'Music',
                                              'Newsletter',
                                              'Notes',
                                              'Paper',
                                              'Presentation',
                                              'Recipe',
                                              'Science',
                                              'Sports',
                                              'Timeline',
                                              'Timesheet',
                                              'Trades',
                                              'To Do List',
                                              'Writer',
                                              ],
                                     value_type=schema.TextLine())

    available_licenses = schema.List(title=_(safe_unicode("Available Licenses")),
                                     default=[
                                         'GNU-GPL-v2 (GNU General Public '
                                         'License Version 2)',
                                         'GNU-GPL-v3+ (General Public License '
                                         'Version 3 and later)',
                                         'LGPL-v2.1 (GNU Lesser General '
                                         'Public License Version 2.1)',
                                         'LGPL-v3+ (GNU Lesser General Public '
                                         'License Version 3 and later)',
                                         'BSD (BSD License (revised))',
                                         'MPL-v1.1 (Mozilla Public License '
                                         'Version 1.1)',
                                         'MPL-v2.0+ (Mozilla Public License '
                                         'Version 2.0 or later)',
                                         'CC-by-sa-v3 (Creative Commons '
                                         'Attribution-ShareAlike 3.0)',
                                         'CC-BY-SA-v4 (Creative Commons '
                                         'Attribution-ShareAlike 4.0 '
                                         'International)',
                                         'AL-v2 (Apache License Version 2.0)',
                                         'Public Domain',
                                         'OSI (Other OSI Approved)'],
                                     value_type=schema.TextLine())

    available_versions = schema.List(title=_(safe_unicode("Available Versions")),
                                     default=['LibreOffice 3.3',
                                              'LibreOffice 3.4',
                                              'LibreOffice 3.5',
                                              'LibreOffice 3.6',
                                              'LibreOffice 4.0',
                                              'LibreOffice 4.1',
                                              'LibreOffice 4.2',
                                              'LibreOffice 4.3',
                                              'LibreOffice 4.4',
                                              'LibreOffice 5.0',
                                              'LibreOffice 5.1',
                                              'LibreOffice 5.2',
                                              'LibreOffice 5.3',
                                              'LibreOffice 5.4',
                                              'LibreOffice 6.0',
                                              'LibreOffice 6.1',
                                              'LibreOffice 6.2',
                                              'LibreOffice 6.3',
                                              'LibreOffice 6.4'],
                                     value_type=schema.TextLine())

    available_platforms = schema.List(title=_(safe_unicode("Available Platforms")),
                                      default=['All platforms',
                                               'Linux',
                                               'Linux-x64',
                                               'Mac OS X',
                                               'Windows',
                                               'BSD',
                                               'UNIX (other)'],
                                      value_type=schema.TextLine())

    model.fieldset('Allowed File Extensions',
                   label=safe_unicode('Allowed file extensions'),
                   fields=['allowed_templatefileextension',
                           'allowed_imagefileextension'])

    allowed_templatefileextension = schema.TextLine(
        title=_(safe_unicode('Allowed Template File Extensions')),
        description=_(safe_unicode(
            'Fill in the allowed template file extensions, '
            'seperated by a pipe \'|\'.')),
    )

    allowed_imagefileextension = schema.TextLine(
        title=_(safe_unicode('Allowed Image File Extensions')),
        description=_(safe_unicode(
            'Fill in the allowed image file extensions, '
            'seperated by a pipe \'|\'.')),
    )

    model.fieldset('instructions',
                   label=u'Instructions',
                   fields=['install_instructions', 'reporting_bugs', ])

    primary('install_instructions')
    install_instructions = RichText(
        title=_(safe_unicode("Template Installation Instructions")),
        description=_(safe_unicode("Please fill in the install instructions")),
        required=False
    )

    primary('reporting_bugs')
    reporting_bugs = RichText(
        title=_(safe_unicode("Instruction how to report Bugs")),
        required=False
    )

    model.fieldset('disclaimer',
                   label=safe_unicode('Legal Disclaimer'),
                   fields=['title_legaldisclaimer', 'legal_disclaimer',
                           'title_legaldownloaddisclaimer',
                           'legal_downloaddisclaimer'])

    title_legaldisclaimer = schema.TextLine(
        title=_(safe_unicode("Title for Legal Disclaimer and Limitations")),
        default=_(safe_unicode("Legal Disclaimer and Limitations")),
        required=False
    )

    legal_disclaimer = schema.Text(
        title=_(safe_unicode("Text of the Legal Disclaimer and Limitations")),
        description=_(safe_unicode(
            "Enter the text of the legal disclaimer and limitations that "
            "should be displayed to the project creator and should be "
            "accepted by the owner of the project.")),
        default=_(safe_unicode(
            "Fill in the legal disclaimer, that had to be accepted by the "
            "project owner")),
        required=False
    )

    title_legaldownloaddisclaimer = schema.TextLine(
        title=_(safe_unicode(
            "Title of the Legal Disclaimer and Limitations for Downloads")),
        default=_(safe_unicode("Legal Disclaimer and Limitations for Downloads")),
        required=False
    )

    primary('legal_downloaddisclaimer')
    legal_downloaddisclaimer = RichText(
        title=_(safe_unicode("Text of the Legal Disclaimer and Limitations for Downlaods")),
        description=_(safe_unicode(
            "Enter any legal disclaimer and limitations for downloads that "
            "should appear on each page for dowloadable files.")),
        default=_(safe_unicode("Fill in the text for the legal download disclaimer")),
        required=False
    )

    primary('information_oldversions')
    information_oldversions = RichText(
        title=_(safe_unicode("Information About Search For Old LibreOffice Versions")),
        description=_(safe_unicode(
            "Enter an information about the search for older "
            "versions of LibreOffice, if they are not on the "
            "versions list (compatibility) anymore.")),
        required=False
    )

    model.fieldset('contactadresses',
                   label=safe_unicode('Special Email Adresses'),
                   fields=['contactForCenter'])

    contactForCenter = schema.ASCIILine(
        title=_(safe_unicode(
            "EMail address for communication with the template center "
            "manager and reviewer")),
        description=_(safe_unicode(
            "Enter an email address for the communication with template "
            "center manager and reviewer")),
        default='templates@libreoffice.org',
        constraint=validateEmail
    )


directives.languageindependent('available_category')
directives.languageindependent('available_licenses')
directives.languageindependent('available_versions')
directives.languageindependent('available_platforms')


# Views


class TUpCenterView(BrowserView):

    def tupprojects(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')

        return catalog(object_provides=ITUpProject.__identifier__,
                       path='/'.join(context.getPhysicalPath()),
                       sort_order='sortable_title')

    def get_latest_program_release(self):
        """Get the latest version from the vocabulary. This only
        goes by string sorting so would need to be reworked if the
        LibreOffice versions dramatically changed"""

        versions = list(self.context.available_versions)
        versions.sort(reverse=True)
        return versions[0]

    def category_name(self):
        category = list(self.context.available_category)
        return category

    def tupproject_count(self):
        """Return number of projects
        """
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')

        return len(catalog(portal_type=(
            'tdf.templateuploadcenter.tupproject',
            'tdf.templateuploaccenter.tupsmallproject'),
                           review_state='published'))

    def tuprelease_count(self):
        """Return number of downloadable files
        """
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')

        return len(catalog(portal_type='tdf.templateuploadcenter.tuprelease'))

    def get_most_popular_products(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        sort_on = 'positive_ratings'
        contentFilter = {
            'sort_on': sort_on,
            'sort_order': 'reverse',
            'review_state': 'published',
            'portal_type': ('tdf.templateuploadcenter.tupproject',
                            'tdf.templateuploadcenter.tupsmallproject')}
        return catalog(**contentFilter)

    def get_newest_products(self):
        self.catalog = api.portal.get_tool(name='portal_catalog')
        sort_on = 'created'
        contentFilter = {
            'sort_on': sort_on,
            'sort_order': 'reverse',
            'review_state': 'published',
            'portal_type': ('tdf.templateuploadcenter.tupproject',
                            'tdf.templateuploadcenter.tupsmallproject')
        }

        results = self.catalog(**contentFilter)

        return results

    def get_products(self, category, version, sort_on, SearchableText=None):
        self.catalog = api.portal.get_tool(name='portal_catalog')
        # sort_on = 'positive_ratings'
        if SearchableText:
            SearchableText = self.munge_search_term(SearchableText)
            contentFilter = {'sort_on': sort_on,
                             'SearchableText': SearchableText,
                             'sort_order': 'reverse',
                             'portal_type': (
                                 'tdf.templateuploadcenter.tupproject',
                                 'tdf.templateuploadcenter.tupsmallproject')}
        else:
            contentFilter = {'sort_on': sort_on,
                             'sort_order': 'reverse',
                             'portal_type': (
                                 'tdf.templateuploadcenter.tupproject',
                                 'tdf.templateuploadcenter.tupsmallproject')}

        if version != 'any':
            # We ask to the indexed value on the project (aggregated from
            # releases on creation/modify/delete of releases)
            contentFilter['releases_compat_versions'] = version

        if category:
            contentFilter['getCategories'] = category

        try:
            return self.catalog(**contentFilter)
        except ParseError:
            return []

    def munge_search_term(self, q):
        for char in BAD_CHARS:
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_chars(r) + '*'
        return r

    def show_search_form(self):
        return 'getCategories' in self.request.environ['QUERY_STRING']


class TUpCenterOwnProjectsViewlet(ViewletBase):

    def get_results(self):
        current_user = api.user.get_current()
        pc = api.portal.get_tool('portal_catalog')
        return pc.portal_catalog(
            portal_type=('tdf.templateuploadcenter.tupproject',
                         'tdf.templateuploadcenter.tupsmallproject'),
            sort_on='Date',
            sort_order='reverse',
            Creator=str(current_user))
