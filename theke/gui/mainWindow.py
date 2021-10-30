import logging

from gi.repository import Gtk
from gi.repository import WebKit2

import theke
import theke.reference

from theke.gui.widget_ThekeGotoBar import ThekeGotoBar
from theke.gui.widget_ThekeHistoryBar import ThekeHistoryBar
from theke.gui.widget_ThekeSearchPane import ThekeSearchPane
from theke.gui.widget_ThekeTableOfContent import ThekeTableOfContent
from theke.gui.widget_ThekeToolsView import ThekeToolsView

# Import needed to load the gui
from theke.gui.widget_ThekeSourcesBar import ThekeSourcesBar
from theke.gui.widget_ThekeDocumentView import ThekeDocumentView

logger = logging.getLogger(__name__)

@Gtk.Template.from_file('./theke/gui/mainWindow.glade')
class ThekeWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "mainWindow"

    _top_box: Gtk.Box = Gtk.Template.Child()
    _statusbar: Gtk.Statusbar = Gtk.Template.Child()

    _ThekeSourcesBar: Gtk.Box = Gtk.Template.Child()
    _ThekeDocumentView : Gtk.Paned = Gtk.Template.Child()

    def __init__(self, navigator):
        super().__init__()

        self._navigator = navigator
        self._setup_view()

        # TODO: Normalement, l'appel de self.show_all() n'est pas nécessaire
        #       car lorsque la fenêtre est créé, la fonction .preset() est appelée
        #       et elle même appelle .show()
        self.show_all()

    def _setup_view(self):

        # TOP
        #   = navigation bar
        #   ... historybar: shortcuts to last viewed documents
        self.historybar = ThekeHistoryBar(on_button_clicked_callback = self.on_history_button_clicked)

        #   ... gotobar: entry to open any document
        self.gotobar = ThekeGotoBar()
        self.gotobar.connect("activate", self.handle_gotobar_activate)
        self.gotobar.autoCompletion.connect("match-selected", self.handle_gotobar_match_selected)

        self._top_box.pack_end(self.gotobar, False, False, 1)
        self._top_box.pack_end(self.historybar, True, True, 1)

        #   ... document view
        self._ThekeDocumentView.finish_setup()
        #   ... document view > TOC
        self._ThekeDocumentView.connect("toc-selection-changed", self.handle_toc_selection_changed)
        # ... document view > webview: where the document is displayed
        self._ThekeDocumentView.register_navigator(self._navigator)
        self._ThekeDocumentView.connect("document-load-changed", self.handle_document_load_changed)
        self._ThekeDocumentView.connect("webview-mouse-target-changed", self.handle_mouse_target_changed)

        #   ... search panel
        #self.searchPane = ThekeSearchPane(builder)

        # self.searchPane.connect("selection-changed", self.handle_searchResults_selection_changed)
        # self.searchPane.connect("start", self.handle_search_start)
        # self.searchPane.connect("finish", self.handle_search_finish)

        # Set size.
        # builder.get_object("searchPane").connect("notify::max-position", self.handle_maxPosition_changed)
        # builder.get_object("tocPane").connect("notify::min-position", self.handle_minPosition_changed)


        # ... tools view
        # self.toolsView = ThekeToolsView(builder)
        # self.toolsView.search_button_connect(self.handle_morphview_searchButton_clicked)
        # self.navigator.connect("click_on_word", self.handle_selected_word_changed)

        # BOTTOM
        #   ... sources bar
        self._ThekeSourcesBar.connect("source-requested", self.handle_source_requested)
        self._ThekeSourcesBar.connect("delete-source", self.handle_delete_source)
        self._navigator.connect("notify::sources", self.handle_sources_updated)
        self._navigator.connect("notify::availableSources", self.handle_availableSources_updated)

        # Set the focus on the webview
        self._ThekeDocumentView.grab_focus()

        # SET ACCELERATORS (keyboard shortcuts)
        accelerators = Gtk.AccelGroup()
        self.add_accel_group(accelerators)

        # ... Ctrl+l: give focus to the gotobar
        key, mod = Gtk.accelerator_parse('<Control>l')
        self.gotobar.add_accelerator('grab-focus', accelerators, key, mod, Gtk.AccelFlags.VISIBLE)
        

    def handle_availableSources_updated(self, object, param) -> None:
        self._ThekeSourcesBar.updateAvailableSources(self._navigator.availableSources)

    def handle_delete_source(self, object, sourceName):
        self._navigator.delete_source(sourceName)

    def handle_gotobar_activate(self, entry):
        '''@param entry: the object which received the signal.
        '''

        ref = theke.reference.parse_reference(entry.get_text().strip())
        if ref.type != theke.TYPE_UNKNOWN:
            self._navigator.goto_ref(ref)

    def handle_gotobar_match_selected(self, entry_completion, model, iter):
        # TODO: give name to column (and dont use a numerical value)
        # Update the text in the GotoBar
        self.gotobar.set_text("{} ".format(model.get_value(iter, 0)))

        # Move the cursor to the end
        self.gotobar.set_position(-1)
        return True

    def handle_document_load_changed(self, obj, web_view, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED:
            # Update the status bar with the title of the just loaded page
            contextId = self._statusbar.get_context_id("navigation")
            self._statusbar.push(contextId, str(self._navigator.title))

            # Update the history bar
            self.historybar.add_uri_to_history(self._navigator.shortTitle, self._navigator.uri)

            # # Update the table of content
            # if self.navigator.toc is None:
            #     self.tableOfContent.hide()
            # else:
            #     self.tableOfContent.set_title(self.navigator.ref.documentName)
            #     self.tableOfContent.set_content(self.navigator.toc.toc)
            #     self.tableOfContent.show()

            # # Hide the morphoView, if necessary
            # if not self.navigator.isMorphAvailable:
            #     self.toolsView.hide()

            # Show the sourcesBar, if necessary
            if self._navigator.ref and self._navigator.ref.type == theke.TYPE_BIBLE:
                self._ThekeSourcesBar.show()
                self._statusbar.hide()
            else:
                self._ThekeSourcesBar.hide()
                self._statusbar.show()

            # if self.navigator.ref and self.navigator.ref.type == theke.TYPE_BIBLE and self.navigator.ref.verse is not None:
            #     self.webview.scroll_to_verse(self.navigator.ref.verse)

    def handle_mouse_target_changed(self, obj, web_view, hit_test_result, modifiers):
        if hit_test_result.context_is_link():
            context_id = self._statusbar.get_context_id("navigation-next")
            self._statusbar.pop(context_id)
            self._statusbar.push(context_id, "{}".format(hit_test_result.get_link_uri()))
        else:
            context_id = self._statusbar.get_context_id("navigation-next")
            self._statusbar.pop(context_id)

    def handle_morphview_searchButton_clicked(self, button):
        self.searchPane.show()
        self.searchPane.search_start(self._navigator.selectedWord.source, self._navigator.selectedWord.strong)

    def handle_searchResults_selection_changed(self, object, result):
        ref = theke.reference.parse_reference(result.reference, wantedSources = self._navigator.sources)
        
        if ref.type == theke.TYPE_UNKNOWN:
            logger.error("Reference type not supported in search results: %s", result.referenceType)
        else:
            self._navigator.goto_ref(ref)

    def handle_search_start(self, object, moduleName, lemma):
        self.toolsView.search_button.set_sensitive(False)

    def handle_search_finish(self, object):
        self.toolsView.search_button.set_sensitive(True)

    def handle_selected_word_changed(self, instance, param):
        w = self._navigator.selectedWord

        self.toolsView.set_morph(w.word, w.morph)

        self.toolsView.set_lemma(w.lemma)
        self.toolsView.set_strongs(w.strong)

        self.toolsView.show()

    def handle_source_requested(self, object, sourceName):
        self._navigator.add_source(sourceName)

    def handle_sources_updated(self, object, params) -> None:
        self._ThekeSourcesBar.updateSources(self._navigator.sources)

    def handle_toc_selection_changed(self, object, tree_selection):
        model, treeIter = tree_selection.get_selected()

        if treeIter is not None:
            self._navigator.goto_section(model[treeIter][1])

    def handle_maxPosition_changed(self, object, param):
        """Move the pane to its maximal value
        """
        object.set_position(object.props.max_position)

    def handle_minPosition_changed(self, object, param):
        """Move the pane to its minimal value
        """
        object.set_position(object.props.min_position)

    def on_history_button_clicked(self, button):
        self._navigator.goto_uri(button.uri)
        return True