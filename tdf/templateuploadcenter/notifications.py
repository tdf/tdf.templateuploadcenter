from plone import api
from tdf.templateuploadcenter.tupcenter import ITUpCenter



def notifiyAboutNewVersion(tupproject, event):
   if hasattr(event, 'descriptions') and event.descriptions:
       for d in event.descriptions:
           if hasattr(d, 'interface') and d.interface is ITUpCenter and 'available_versions' in d.attributes:
               users=api.user.get_users()
               message='We added a new version of LibreOffice to the list.\n' \
                       'Please add this version to your LibreOffice template release(s), ' \
                       'if it is (they are) compatible with this version.\n\n' \
                       'Kind regards,\n\n' \
                       'The LibreOffice Extension and Template Site Administration Team'
               for f in users:
                   mailaddress = f.getProperty('email')
                   api.portal.send_email(
                       recipient=mailaddress,
                       sender="noreply@libreoffice.org",
                       subject="Templates Section: New Version of LibreOffice Added",
                       body=message,
                   )