from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib

import theke.index
import theke.externalCache
import theke.templates

import logging
logger = logging.getLogger(__name__)

class ThekeArchivist(GObject.GObject):
    """The archivist indexes and stores documents
    """

    def __init__(self) -> None:
        self._index = theke.index.ThekeIndex()

    def update_index(self, force = False):
        """Update the index
        """
        indexBuilder = theke.index.ThekeIndexBuilder()
        indexBuilder.build(force)
    
    def get_document_handler(self, ref, sources):
        """Return a handler providing an input stream to the document
        """

        if ref.type == theke.TYPE_INAPP:
            logger.debug("Get a document handler [inApp] : {}".format(ref))
            file_path = './assets/{}'.format(ref.inAppUriData.fileName)
            return FileHandler(file_path)

        if ref.type == theke.TYPE_BOOK:
            logger.debug("Get a document handler [external book] : {}".format(ref))
            # For now, can only open the first source
            source = sources[0]
            document_path = theke.externalCache.get_best_source_file_path(source.name, relative=True)

            content = theke.templates.render('external_book', {
                'ref': ref,
                'document_path': document_path})
            
            return ContentHandler(content)

        return None

    ### API: proxy to the ThekeIndex
    def list_external_documents(self):
        """List external documents from the index
        """
        return self._index.list_external_documents()

    def list_documents_by_type(self, documentType):
        """List documents from the index by type
        """
        return self._index.list_documents_by_type(documentType)

    def list_sword_sources(self, contentType = None):
        """List sources from the index

        @param contentType: theke.index.MODTYPE_*
        """
        return self._index.list_sources(theke.index.SOURCETYPE_SWORD, contentType)

class ContentHandler():
    def __init__(self, content) -> None:
        self._content = content

    def get_input_stream(self):
        return Gio.MemoryInputStream.new_from_data(self._content.encode('utf-8'))

class FileHandler():
    def __init__(self, filePath) -> None:
        self._filePath = filePath

    def get_input_stream(self):
        return Gio.File.new_for_path(self._filePath).read()
