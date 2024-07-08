# -*- coding: utf-8 -*-
#pylint: disable=C0413, E1101
"""
kategori referring from araclar.py in notebook
"""
from gi.repository import Gio, GObject, GLib
from gi.repository import Gtk as gtk
from araclar import CATEG, get_stock

class Category(GObject.Object):
    """
    define gobject propery to index list
    """
    __gtype_name__ = 'Category'

    def __init__(self, category_id, category_name):
        super().__init__()

        self.category_id = category_id
        self.category_name = category_name
        self.check = {1:None}

    @GObject.Property
    def name_id(self):
        """
        returns id
        """
        return self.category_id

    @GObject.Property
    def name(self):
        """
        returns name
        """
        return self.category_name

class CategoryWindow(gtk.Window):
    """
    build, create and show categoreis
    """
    checklist = {} # gives a list of check button in relation to categories window

    def __init__(self, app, set_text):

        gtk.Window.__init__(self, application=app)
        self.set_text = set_text

        self.set_modal(True)
        self.set_resizable(False)
        self.set_title("Categoreis")

        headerbar = gtk.HeaderBar()
        self.set_titlebar(headerbar)

#right side
        box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        box.set_margin_end(42)
        box.set_spacing(24)
        box.props.margin_top = 28
        box.props.margin_bottom = 0

#left side
        info_image, info_label = self.make_info(box)
        hbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        hbox.set_spacing(36)
        hbox.props.margin_top = 32
        hbox.props.margin_bottom = 32

        bilgi = self.make_combobox(box)

        for order in range( 1, len( bilgi ) + 1 ):
            label = list(CATEG)[order-1]
            self.checklist[order] = gtk.CheckButton(label=label)
            self.checklist[order].connect("toggled", self.toogle_change,
                bilgi, info_image, info_label, label )
            hbox.append( self.checklist[ order ] )

        dume = gtk.Button( label="Apply" )
        dume.connect( "clicked", lambda _: self.check_clicked( bilgi ) )
        dume.set_margin_top(16)
        dume.set_margin_start(32)
        dume.set_margin_end(32)

        kutu = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        kutu.set_margin_top(22)
        kutu.set_margin_start(46)
        kutu.set_margin_end(0)
        kutu.set_spacing(22)
        kutu.append(hbox)
        kutu.append(box)

        last_box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        last_box.set_margin_bottom(22)
        last_box.set_spacing(12)

        last_box.append(kutu)
        last_box.append(dume)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.ALWAYS)
        sw.set_size_request( 450, 450)
        sw.set_child(last_box)

        self.set_child(sw)
        self.add_css_class("wiki-form")
        self.set_transient_for(app.win)
        self.present()

    def toogle_change(self, *args):
        """
        set active checkbox
        """
        w, bilgi, info_image, info_label, label = args


        def get_down(label):
            """
            get down your rocking thee...
            """
            return bilgi[list(CATEG).index(label) +1]

        drop_down =  get_down(label)
        drop_down.set_tooltip_markup(f"<big>{label}</big>")

        active = None
        for each in self.checklist.values():
            if each.get_active():
                active = True
                break
        if active:
            GLib.idle_add(info_image.set_visible, False)
            GLib.idle_add(info_label.set_visible, False)

            for each in bilgi.values():
                GLib.idle_add(each.set_visible, True)

        else:
            GLib.idle_add(info_image.set_visible, True)
            GLib.idle_add(info_label.set_visible, True)

            for each in bilgi.values():
                GLib.idle_add(each.set_visible, False)
                GLib.idle_add(each.set_sensitive, False)

        if w.get_active():
            GLib.idle_add(get_down(w.get_label()).set_sensitive,True)
            return True
        GLib.idle_add(get_down(w.get_label()).set_sensitive, False)
        return False

    def make_info(self, box):
        """
        make infobox for categories
        """
        info_image = get_stock("wiki-editor-symbolic", size=172)
        info_image.set_valign(gtk.Align.START)
        info_label = gtk.Label()
        info_label.set_markup("\n<big><i>"
            "<b>Choose categoreis for your writing</b>\n"
            "\nPick one to insert into your text\n\n"
            "</i></big>"
            "<i><u>Note that:</u>\t"
            "Both selected and checked will be inserted.\n"
            "Multiple item check also allowed in dropdown.\n"
            "Click on each label to have multiple selection... </i>"
        )
        box.append(info_label)
        box.append(info_image)
        return info_image, info_label

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
            drop_down.set_visible(False)
            drop_down.set_sensitive( False)
       #     drop_down.set_enable_search(True)
        #    drop_down.set_search_match_mode(2)

            bilgi[order] = drop_down

            for liste in CATEG[kategori]:
                list_store.append(  Category(
                    category_name=liste,
                    category_id= kategori )
                )

            factory.connect("setup", self.create_item_box)
            factory.connect("bind", self.set_item_created, drop_down)

            box.append(drop_down)

        return bilgi

    def create_item_box(self, _, list_item):
        """
        custom widget for arrowdown
        """
        box = gtk.Box()
        box.append( get_stock("emblem-documents-symbolic") )
        box.append(gtk.Label())
        check =  gtk.CheckButton()
        check.set_child(box)
        box.set_spacing(12)
        box.props.margin_start = 12
        box.props.margin_end = 12


        event = gtk.GestureClick.new()
        box.add_controller(event)
        event.connect("unpaired-release",
            lambda *_: check.emit("activate"))

        list_item.set_child(check)

    def set_item_created(self, _, set_item_created,drop_down):
        """
        setup for custom created item
        in arrow down
        ...
        """
        check = set_item_created.get_child()
        box = check.get_child()
        label = box.get_last_child()


        event = gtk.GestureClick.new()
        check.add_controller(event)

        for each in "pressed", "unpaired-release","released":
            event.connect(each, lambda *_:
                drop_down.set_selected(set_item_created.get_position())
            )

        item = set_item_created.get_item()

        check.connect("toggled", lambda i:
            item.check.update({1:i.get_active()}) )

        label.set_text(item.category_name)

    def insert_text(self, *args):
        """
        find and insert each category
        """
        bilgi, number, check = args

        category_class = bilgi[number].get_selected_item()
        konu = category_class.name
        store =  bilgi[number].get_model()

        checked_items = []
        for _index in range(store.get_n_items()):
            each_item = store.get_item(_index)
            if check.get_label() == each_item.name_id and each_item.check[1]:
                checked_items.append(f"[[Category:{each_item.name}]]")

        if f"[[Category:{konu}]]" not in checked_items:
            checked_items.append(f"[[Category:{konu}]]")

        self.set_text(
            f"\n[[Category:{check.get_label()}]]\n"
            f"{"\n".join(checked_items)}",
            True, color="#446FA2")

    def check_clicked(self, bilgi):
        """
        insert chosen into wikitext
        """

        for number, check in self.checklist.items():
            if check.get_active():
                self.insert_text(bilgi, number, check)

        self.destroy()
