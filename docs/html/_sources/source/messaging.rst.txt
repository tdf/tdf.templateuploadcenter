Messaging
#########

The tdf.templateuploadcenter Plone add-on use some of the Plone messaging
implementations to create messages to the site admin, reviewers and the
owner / creator of templates / template projects.

Messages To The Site-Admininstrator / Administrator
***************************************************

- The site-administrator / admininstrator get an e-mail once a new template
  project or small template project have been added to the Template Center.
- If the project owner submit her / his project or small project for
  publication, the  site-administrator / administrator get an e-mail
  about this event.
- Once the text of a published project or a small project changes the
  site-administrator /  administrator will get an e-mail with the complete
  text of the project or small project summary and its description. Thus he
  get an  information, if the text of the project or the small project
  changes into a direction that has not been reviewed.

If the form field 'contactForCenter' in the Template Center contains an
e-mail address the above messages will be send to this address. Otherwise
the e-mail goes to the e-mail address of the Plone site.



Messages To The Project Owner Or Small Project Owner
****************************************************

- Once a workflow status of his project(s) or small project(s) change the
  project owner or small project owner will get a message (e-mail) which
  inform her / him about this new status.
- The project owner will get an e-mail once a template release or a linked
  template release have been added to her / his project(s).
- Once the site-administrator / administrator of the Plone site adds a new
  LibreOffice (product) version to the form field 'Available Versions' the
  owner of a project or small project will get an e-mail to inform her / him
  about this event. The message ask the owner to update the versions list
  of the (linked) releases of his project(s).






