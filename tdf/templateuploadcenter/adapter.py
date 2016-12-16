from plone.indexer import indexer
from tdf.extensionuploadcenter.adapter import IReleasesCompatVersions
from tdf.extensionuploadcenter.adapter import ReleasesCompatVersions
from tdf.templateuploadcenter.tupproject import ITUpProject
from zope.component import adapter
from zope.interface import implementer


@implementer(IReleasesCompatVersions)
@adapter(ITUpProject)
class TemplateReleasesCompatVersions(ReleasesCompatVersions):
    """ Clone the extensions project adapter for templates """


@indexer(ITUpProject)
def releases_compat_versions(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return IReleasesCompatVersions(context).get()
