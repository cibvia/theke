from gi.repository import Gtk

import theke
import theke.uri
import theke.index

# from collections import namedtuple
# tocFields = namedtuple('tocFields',['name','rawUri'])

def get_toc_BIBLE(ref):
    #TODO:  /!\ Suppose que la référence est une référence biblique.
    #       Cette fonction devra être adaptée aux livres non bibliques.

    thekeIndex = theke.index.ThekeIndex()
    nbOfChapters = thekeIndex.get_biblical_book_nbOfChapters(ref.documentName)

    toc = ThekeTOC(type_of_toc = theke.TYPE_BIBLE)

    for i in range(1, nbOfChapters + 1):
        #uri = theke.uri.build('sword', ['', theke.uri.SWORD_BIBLE, '{} {}'.format(ref.documentName, i+1)], sources = ref.sources)
        #toc.append(str(i+1), uri.get_encoded_URI())
        toc.append(str(i), i)

    return toc

class ThekeTOC():
    def __init__(self, type_of_toc = 0) -> None:
        if type_of_toc == theke.TYPE_BIBLE:
            self.toc = Gtk.ListStore(str, int)
        else:
            raise("Unknown type of TOC")

        self.type = type_of_toc

    def append(self, label, data) -> None:
        """Append an entry to the table of content

        @param label: name of the entry
        @param data: data needed to jump to this entry (section number, uri, ...)
        """
        return self.toc.append((label, data))
