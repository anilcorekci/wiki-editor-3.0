# -*- coding: utf-8 -*-
#pylint: disable=C0413, E1101
"""
kategori referring from araclar.py in notebook
"""
from gi.repository import Gio, GObject
from gi.repository import Gtk as gtk
from araclar import CATEG, get_stock

class Category(GObject.Object):
    __gtype_name__ = 'Category'

    def __init__(self, category_id, category_name):
        super().__init__()

        self.category_id = category_id
        self.category_name = category_name

    @GObject.Property
    def name_id(self):
        return self.category_id

    @GObject.Property
    def name(self):
        return self.category_name

class CategoryWindow(gtk.ApplicationWindow):
    """
        build, create and show categoreis
    """
    checklist = {} # gives a list of check button in relation to categories window

    def __init__(self, app, set_text):

        gtk.ApplicationWindow.__init__(self, application=app)
        self.set_text = set_text

        self.set_modal(True)
        self.set_resizable(False)
        self.set_title("Yazınız İçin Kategori")

        headerbar = gtk.HeaderBar()
        self.set_titlebar(headerbar)

        box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        box.set_margin_end(20)
        box.set_margin_bottom(20)
        box.set_spacing(32)

        hbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        hbox.set_spacing(41)

        bilgi = self.make_combobox(box)

        for order in range( 1, len( bilgi ) + 1 ):
            self.checklist[order] = gtk.CheckButton()
            hbox.append( self.checklist[ order ] )

        dume = gtk.Button( label="Tamam" )
        dume.connect( "clicked", lambda _: self.check_clicked( bilgi ) )
        dume.set_margin_top(16)
        dume.set_margin_start(32)
        dume.set_margin_end(32)

        kutu = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        kutu.set_margin_top(30)
        kutu.set_margin_start(46)
        kutu.set_margin_end(32)
        kutu.set_spacing(18)
        kutu.append(hbox)
        kutu.append(box)

        last_box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        last_box.set_margin_bottom(22)
        last_box.append(kutu)
        last_box.append(dume)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.ALWAYS)
        sw.set_size_request( last_box.get_width(), 350)
        sw.set_child(last_box)

        self.set_child(sw)
        self.add_css_class("wiki-form")
        self.set_transient_for(app.win)
        self.present()

    def make_combobox(self, box):
        """
        append each given category list
        into each new combobox
        ...
        """
        bilgi = {}

        for kategori, order in zip( CATEG, range( 1, len(CATEG) + 1 ) ):

            factory = gtk.SignalListItemFactory()
            list_store = Gio.ListStore(item_type=Category)

            drop_down = gtk.DropDown(model=list_store, factory=factory)
            drop_down.set_size_request(300,-1)

            bilgi[order] = drop_down

            for liste in CATEG[kategori]:
                list_store.append(  Category(
                    category_name=liste,
                    category_id= CATEG[kategori] )
                )

            factory.connect("setup", self.create_item_box )
            factory.connect("bind", self.set_item_created)

            box.append(drop_down)

        return bilgi

    def create_item_box(self, _, list_item):
        """
        custom widget for arrowdown
        """
        box = gtk.Box()
        box.append( get_stock("emblem-documents-symbolic") )
        box.append(gtk.Label())
        box.set_spacing(12)
        box.props.margin_start = 12
        box.props.margin_end = 12
        list_item.set_child(box)

    def set_item_created(self, _, set_item_created):
        """
        setup for custom created item
        in arrow down
        ...
        """
        box = set_item_created.get_child()
        label = box.get_last_child()
        label.set_text(set_item_created.get_item().category_name)

    def check_clicked(self, bilgi):
        """
        insert chosen into wikitext
        """

        for number, check in self.checklist.items():
            if check.get_active():
                category_class = bilgi[number].get_selected_item()
                konu = category_class.name
                self.set_text(f"[[kategori:{konu}]]\n",
                    True, color="#446FA2")

        self.destroy()
