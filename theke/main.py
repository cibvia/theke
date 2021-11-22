from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import GLib

import os
import theke
import theke.gui.mainWindow
import theke.index
import theke.navigator
import theke.sword
import theke.templates
import theke.uri

import logging
logger = logging.getLogger(__name__)

class ThekeApp(Gtk.Application):
    def __init__(self):
        logger.debug("ThekeApp - Create a new instance")

        Gtk.Application.__init__(self,
                                 application_id="com.github.a2ohm.theke",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.add_main_option(
            "debug",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Print debug messages",
            None,
        )

        self._window = None
        self._navigator = None

    def do_startup(self):
        """Sets up the application when it first starts
        """
        logger.debug("ThekeApp - Do startup")

        Gtk.Application.do_startup(self)

        # Create some directories
        for path in [theke.PATH_ROOT, theke.PATH_DATA, theke.PATH_EXTERNAL]:
            if not os.path.isdir(path):
                logger.debug("ThekeApp − Make dir : %s", path)
                os.mkdir(path)

        # Index sword modules
        indexBuilder = theke.index.ThekeIndexBuilder()
        indexBuilder.build(force = False)

    def do_activate(self):
        """Shows the default first window of the application (like a new document).
        This corresponds to the application being launched by the desktop environment
        """
        logger.debug("ThekeApp - Do activate")

        # Set the navigator
        self._navigator = theke.navigator.ThekeNavigator()

        if not self._window:
            logger.debug("ThekeApp - Create a new window")
            self._window = theke.gui.mainWindow.ThekeWindow(navigator = self._navigator)
            self._window.set_application(self)
            self._window.present()

        # From the index ...
        thekeIndex = theke.index.ThekeIndex()

        # ... load the list of modules
        # TODO: pour l'usage qui en est fait, il serait préférable de créer la fonction
        #       thekeIndex.list_sword_modules()
        bible_mods = thekeIndex.list_sources(sourceType = theke.index.SOURCETYPE_SWORD, contentType = theke.sword.MODTYPE_BIBLES)
        book_mods = thekeIndex.list_sources(sourceType = theke.index.SOURCETYPE_SWORD, contentType = theke.sword.MODTYPE_GENBOOKS)

        # ... load the list of external documents
        external_docs = thekeIndex.list_external_documents()

        # ... populate the gotobar autocompletion list
        for documentData in thekeIndex.list_documents_by_type(theke.TYPE_BIBLE):
            self._window._ThekeGotoBar.append((documentData.name, 'powder blue'))

        for documentData in thekeIndex.list_documents_by_type(theke.TYPE_BOOK):
            self._window._ThekeGotoBar.append((documentData.name, 'white smoke'))

        # Register application screens in the GotoBar
        # for inAppUriKey in theke.uri.inAppURI.keys():
        #     self.window.gotobar.append((inAppUriKey, 'sandy brown'))

        # Build templates
        theke.templates.build_template('welcome', {'BibleMods': bible_mods})
        theke.templates.build_template('modules', {'BibleMods': bible_mods, 'BookMods' : book_mods})
        theke.templates.build_template('external_documents', {'ExternalDocs': external_docs})

        # Load the main screen
        uri = theke.uri.parse(theke.URI_WELCOME, isEncoded=True)
        self._navigator.goto_uri(uri)
