from plone.dexterity.content import Item


class ReleaseCustomName(Item):

    """Custom name for a release and linked release from the title and the release number"""

    @property
    def title(self):
        if hasattr(self, 'projecttitle') and hasattr(self, 'releasenumber'):
            # Guard required for migration
            if self.projecttitle is None:
                self.projecttitle = ''
            return self.projecttitle + ' - ' + self.releasenumber
        else:
            return ''

    def setTitle(self, value):
        return
