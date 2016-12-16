from plone import api
from tdf.extensionuploadcenter.adapter import IReleasesCompatVersions

import logging

logger = logging.getLogger(__name__)


def populat_release_compat_version_index(context):
    pc = api.portal.get_tool(name='portal_catalog')

    # Search for all projects:
    projects = pc.searchResults({
        'portal_type': 'tdf.templateuploadcenter.tupproject'
    })

    for brain_project in projects:
        project = brain_project.getObject()
        query = '/'.join(project.getPhysicalPath())
        brains = pc.searchResults({
            'path': {'query': query, 'depth': 1},
            'portal_type': ['tdf.templateuploadcenter.tuprelease',
                            'tdf.templateuploadcenter.tupreleaselink']
        })

        result = []
        for brain in brains:
            if isinstance(brain.compatibility_choice, list):
                result = result + brain.compatibility_choice

        IReleasesCompatVersions(project).set(list(set(result)))
        logger.info('Updated project {}'.format(project.id))
