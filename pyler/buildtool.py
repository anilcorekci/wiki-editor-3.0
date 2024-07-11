# -*- coding: utf-8 -*-
#pylint: disable=E1101
"""
TOOL BUTTON BUILD FOR ARACLAR
"""

from gi.repository import Gtk as gtk
from gi.repository import Gio
from gi.repository import Pango as pango


from kategori import CategoryWindow
from araclar import mesaj

class ToolItem():
    """
    create tooltiem via getting args:
    """
    shortcut = None
    event = None
    label = None
    app = None
    item = None

    def __init__(self, *args):
        
        if len(args) > 5:
            self.wikieditor, self.label, tooltip, resim, islem, self.shortcut= args

        else:
            self.wikieditor, self.label, tooltip, resim, islem = args

        self.app = self.wikieditor.app
        self.add_custom_styling = self.wikieditor.add_custom_styling

        self.item = self.make_item(resim, self.label, tooltip)
        self.connect_function(self.item, islem)
        self.add_shortcut()

        self.wikieditor.gl_b["tool_active"].append(self.item)

    def make_item(self, resim, label, tooltip ):
        """
        make custom box with flowbox and box
        return item
        """
        button = gtk.Button()
        box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        box.set_spacing(6)
        box.set_size_request(32,32)
        box.set_can_focus(False)

        label = gtk.Label(label=label)

        resim.set_margin_top(3)
        resim.set_pixel_size(24)
        box.set_halign(gtk.Align.CENTER)
        box.append(resim)
        box.append(label)

        button.set_child(box)
        button.set_tooltip_text(tooltip)
        button.add_css_class("toolitem")
        return button

    def connect_function(self, item, islem):
        """
        #add gtk event to item
        parse type of islem and
        connect fuctions
        """
      #  self.event = gtk.GestureClick.new()
       # item.add_controller(self.event)

        type_of = type(islem)

        match type_of:
            case type_of if type_of is dict:
                # if islem is a dict unpack & call sablon
                shortcut, format_ = list( i for i in islem.items() )[0]
                item.connect('clicked',
                    lambda *_: self.sablon(shortcut, format_))
                self.shortcut = shortcut

            case type_of if type_of is list:
                item.connect('clicked',
                    lambda *_: self.list_action(islem) )

                if len(islem) == 3:
                    self.shortcut = islem[2]

            case type_of if type_of is str:
                # if it's a string call it
                # as a fuction within ToolItem class
                item.connect('clicked', getattr(self, islem))

            case type_of if callable(type_of):
                item.connect('clicked',islem )

    def add_shortcut(self):
        """
        add shortcut if any key given
        ...
        """
        if not self.shortcut:
            self.wikieditor.hamburgers[2].add_to_menu(
                self.label,
                lambda *_:
                self.event.emit("pressed", True, True, True )
            )

            return False

        self.item.set_tooltip_text(
                self.item.get_tooltip_text() + \
                "\n  Shortcut: " +\
                f"{self.shortcut}"
            )

        action = Gio.SimpleAction.new(self.label, None)
        action.connect("activate", lambda *_: self.event.emit("pressed"))

        self.app.set_accels_for_action( f"win.{self.label}", [self.shortcut] )

        self.wikieditor.hamburgers[2].add_to_menu(
            self.label,
            lambda *_:
            self.event.emit("pressed", True, True, True )
        )

    #        print(self.label,"************",self.shortcut)
        return True

    def list_action(self, islem):
        """
        # if islem is a list modify selection_ of text
        """
        if self.wikieditor.get_konu():
            self.wikieditor.set_text(
                [f"{islem[0]}",
                f"{self.wikieditor.get_konu()}",
                f"{islem[1]}" ]
            )
        else:
            self.wikieditor.ileti.set_text("No selected text!")

    def sablon(self, _, format_):
        """
        Build text form from given list
        """
        pencere = gtk.Window(application=self.app)
        pencere.set_opacity(0.99)

        title = f"{format_.split('|')[0].strip('{').upper()}"
        pencere.set_title(title)

        pencere.set_titlebar(gtk.HeaderBar())
        pencere.set_modal(True)

        vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        box = gtk.Box(orientation=gtk.Orientation.VERTICAL)

        create_form = {}
        range_ = len(format_.split("{}"))  # number of entries
        entry, label = [ [1, range_], [range_, range_*2]]

        for each_en, each_lb in zip(range(*entry), range(*label) ):

            text = f"{format_.split('{}')[each_en -1 ]}"
            text = text.strip("{}=''").replace("|"," ").replace("_"," ").title()

            create_form[each_lb] = gtk.Label(use_markup=True, label=f"<big>{text}</big>", xalign=0)
            create_form[each_lb].set_size_request(200,-1)

            create_form[each_en] = gtk.Entry()
            create_form[each_en].set_hexpand(True)
            create_form[each_en].set_size_request(260,-1)

            hb = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
            hb.append( create_form[each_lb] )
            hb.append( create_form[each_en] )
            box.append(hb)

        ekle = gtk.Button(label=" Apply ")
        ekle.set_margin_top(42)
        ekle.set_margin_bottom(32)
        ekle.set_margin_start(32)
        ekle.set_margin_end(32)

        ekle.connect("clicked", lambda _:
            self.set_en_label_text(create_form, entry, label, format_, pencere) )

        vbox.append(box)
        vbox.append(ekle)

        box.set_spacing(32)
        box.set_margin_top(32)
        box.set_margin_start(48)
        box.set_margin_bottom(13)
        box.set_margin_end(32)

        pencere.set_resizable(False)

        sw = gtk.ScrolledWindow()
        sw.set_child(vbox)
        sw.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.ALWAYS)
        sw.set_size_request( vbox.get_width(), 300)
        pencere.set_child(sw)

        pencere.add_css_class( "wiki-form")
        pencere.set_transient_for(self.wikieditor)
        self.wikieditor.add_custom_styling(pencere)

        pencere.present()

    def set_en_label_text(self, *args):
        """
        order and apply actions taken from ui window
        """

        create_form, entry, label, format_, pencere = args

        get_text = []
        for each_en, each_lb in zip(range(*entry), range(*label) ):

            if not create_form[each_en].get_text():
                mesaj(f"{ create_form[each_lb].get_text() }"
                      "\n Must be filled!", 
                      pencere, style=self)
                return False

            get_text.append(create_form[each_en].get_text() + "\n")

        self.wikieditor.set_text(format_.format(*get_text), True, color="#B17132")
        pencere.set_transient_for(self.wikieditor)
        pencere.destroy()
        return True

    def color_select(self, *_):
        """
        build and show color selection apply to text with <span color>
        """
        if not self.wikieditor.get_konu():
            return False

        konu = self.wikieditor.get_konu()

        renksec = gtk.ColorChooserDialog()
        renksec.set_property('show-editor', False)
        renksec.set_title("Select a color")
        renksec.set_transient_for(self.wikieditor)
        renksec.set_modal(True)

        def set_color(_, response=None):
            """
            select color convert to rgba in span
            """
            rgba = renksec.get_rgba()
            rgb = [ str( int(i * 255) ) for i in [rgba.red, rgba.green, rgba.blue ] ]
            rgba = ", ".join([*rgb, str( round(rgba.alpha,3) )])

            if response == gtk.ResponseType.OK:
                self.wikieditor.set_text([f'<span style="color:rgba({rgba});">',
                f"\n{konu}\n","</span>"], color=f"rgba({rgba})")
            renksec.destroy()

        renksec.connect("response", set_color)
        self.wikieditor.add_custom_styling(renksec)
        renksec.show()
        return True

    def kategori(self, *_):
        """call category window from kategori"""
        window = CategoryWindow(self.app, self.wikieditor.set_text)
        self.wikieditor.add_custom_styling(window)

    def font_select(self, *_):
        """
        build and show font selection apply to text with <span color>
        """
        if not self.wikieditor.get_konu():
            return False

        bounds, konu = self.wikieditor.get_konu(have_bounds=True)

        def set_font(font_desc):
            """
            insert font in span taken 
            from pango font_desc
            """
            styles = ["normal","oblique", "italic"]

            family = font_desc.get_family()
            size_ = str( font_desc.get_size() ) [0:2]
            style = styles[ int( font_desc.get_style() ) ]
            weight = int( font_desc.get_weight() )

            if not self.wikieditor.get_konu():
                self.wikieditor.current_buffer.select_range(*bounds)

            self.wikieditor.set_text(
                [f'<span style="font-family:{family};'
                f"font-size:{size_}px;"
                f"font-style:{style};"
                f'font-weight:{weight}">',
                f"\n{konu}\n",  "</span>"],
                font=font_desc)

        dialog = gtk.FontDialog()
        dialog.set_modal(True)

        font = pango.FontDescription.new()
        can = Gio.Cancellable.new()

        def finish( _, task): #font_dialog#task
            """
            get_font value on finish
            """
            if  task.had_error():
                return False

            font_desc = dialog.choose_font_finish(task)
            set_font(font_desc)
            return True

        dialog.choose_font(self.app.win, font, can, finish)
