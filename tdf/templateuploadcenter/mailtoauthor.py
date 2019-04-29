# -*- coding: utf-8 -*-
from plone.autoform.form import AutoExtensibleForm
from zope import interface
from zope import schema
from zope import component
from z3c.form import form, button
import re
from zope.interface import Invalid

from Products.statusmessages.interfaces import IStatusMessage

from tdf.templateuploadcenter import MessageFactory as _


checkemail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match


def validateemail(value):
    if not checkemail(value):
        raise Invalid(_(u"Invalid email address"))
    return True



class MailToAuthorSchema(interface.Interface):

    inquirerfirstname = schema.TextLine(
        title=_(u"Your First Name"),
        description=_(u"Please fill in your first name(s)")
    )

    inquirerfamilyname = schema.TextLine(
        title=_(u"Your Family Name"),
        description=_(u"Please fill in your familiy name")
    )

    inquireremailaddress = schema.TextLine(
        title=_(u"Your Email Address"),
        description=_(u"Please fill in your email address."),
        constraint=validateemail
    )

    projectname = schema.TextLine(
        title=_(u"Project Name"),
        description=_(u"The name of the project, to which author you want "
                      u"to send feedback.")
    )

    inquiry = schema.Text(
        title=_(u"Your Message To The Author"),
        description=_(u"What is your message to the author of the project? "
                      u"Your message is limited to 1000 characters."),
        max_length=1000
    )


class MailToAuthorAdapter(object):
    interface.implements(MailToAuthorSchema)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.inquirerfirstname = None
        self.inquirerfamilyname = None
        self.inquireremailaddress = None
        self.projectname = None
        self.inquiry = None


class MailToAuthorForm(AutoExtensibleForm, form.Form):
    schema = MailToAuthorSchema
    form_name = 'authormail_form'

    label = _(u"Mail To The Project Author")
    description = _(u"Contact the project author and send your feedback")

    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)

        # call the base class version - this is very important!
        super(MailToAuthorForm, self).update()

    @button.buttonAndHandler(_(u'Send Email'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Redirect back to the front page with a status message

        IStatusMessage(self.request).addStatusMessage(
                _(u"We send your message to the author of the project. It's "
                  u"on his choice, if he'll get back to you."),
                "info"
            )

        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
            """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
