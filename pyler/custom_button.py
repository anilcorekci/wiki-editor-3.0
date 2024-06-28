# -*- coding: utf-8 -*-
#pylint: disable=E1101
"""
custom button for menus
"""
from gi.repository import Gtk as gtk
from gi.repository import Gio, GLib

class MakeHamburger(gtk.MenuButton):
    """
    yummy :P
    """
    ex_menu = None
    n_time = 0

    def __init__(self, window, label=None, icon=None):

        gtk.MenuButton.__init__(self)
        self.window = window
        self.menu = Gio.Menu.new()

        popover = gtk.PopoverMenu()  # Create a new popover menu
        popover.set_menu_model(self.menu)

        self.set_popover(popover)

        if icon:
            self.set_icon_name(icon)

        if label:
            self.set_label(label)

    def add_to_menu(self, *args, **kwargs): #name, funk, shortcut, ):
        """
        add to menu
        """
        default = { 'sub': None, 'check': None }
        kwargs = { **default, **kwargs }

        for i, item in enumerate(args):
            match i:
                case 0:
                    name = item.replace(" ","__")
                case 1:
                    funk = item
                case 2 if item:
                    #add shortcut
                    self.window.app.set_accels_for_action( f"win.{name}", [item] )
                case i if i >= 3:
                    key = list(default.keys())[i-3]
                    kwargs[key] = item

        for item, val in kwargs.items():
            match item:
                case "sub" if val:
                    val.append(name.replace("__"," "), f"win.{name}")

                case "sub" if not val:
                    self.menu.append(name.replace("__"," "), f"win.{name}")

                case "check" if val:
                    action = Gio.SimpleAction.\
                        new_stateful(name, None, GLib.Variant.new_boolean(False))

                case "check" if not val:
                    action = Gio.SimpleAction.new(name, None)

        action.connect("activate", funk)
        self.window.add_action(action)

    def to_sub_menu(self, menu_name ):
        """
        'append', 'append_item', 'append_section', 'append_submenu
        """
        if isinstance(menu_name, Gio.Menu):
            self.ex_menu = self.menu
            self.menu = menu_name
            return False

        if self.ex_menu:
            self.n_time += 1

        if self.ex_menu and self.n_time == 2:
            self.menu = self.ex_menu
            self.ex_menu = None

        sub = Gio.Menu.new()
        menu_name = menu_name.replace(" ","__")
        self.menu.append_submenu(menu_name.replace("__"," "), sub)
        return sub

class ToolBar(gtk.Box):
    """
    create toolbar widget
    """
    appearance = "BOTH"
    position = "LEFT"
    options = "BOTTOM", "TOP", "RIGHT", "LEFT"
    orientation = None #for toolbar position

    def __init__(self):
        gtk.Box.__init__(self)

        self.set_orientation( gtk.Orientation.VERTICAL )

        self.sw = gtk.ScrolledWindow()
        self.sw.set_child(gtk.Frame(child=self) )
        self.sw.set_propagate_natural_width(True) ##!
        self.sw.set_propagate_natural_height(True) ##!
        self.sw.set_policy( gtk.PolicyType.EXTERNAL, True )

        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_spacing(13)
        self.set_margin_top(6)

        self.sw.add_css_class( "wiki-scroll" )

    @property
    def scroll(self):
        """
        return parent widget
        """
        return self.sw

    def get_position(self):
        """
        returns current orientation
        """
        return self.position

    def set_position(self, position):
        """
        set the position of toolbar
        "BOTTOM", "TOP", "RIGHT", "LEFT"
        """
        if position not in self.options:
            raise KeyError

        if self.position == position:
            return False

        while self.position != position:
            self.change_tool()

        return True

    def change_tool(self, *_):
        """
        set toolbar position left/right/bottom/top
        """
        app = self.get_root()
        self.orientation = not self.orientation

        first = app.horizontal.get_first_child()
        last = app.horizontal.get_last_child()

        if self.orientation:
            app.horizontal.reorder_child_after(first, last)
            app.horizontal.set_orientation(gtk.Orientation.VERTICAL)
            self.set_orientation(gtk.Orientation.HORIZONTAL)
            self.set_homogeneous(True) #bottom and top position

        else:
            app.horizontal.reorder_child_after(last, first )
            app.horizontal.set_orientation(gtk.Orientation.HORIZONTAL)
            self.set_orientation(gtk.Orientation.VERTICAL)
            self.set_homogeneous(False) #right and left position

        match self.position:
            case "LEFT":
                self.position = "BOTTOM"
            case "RIGHT":
                self.position = "TOP"
            case "BOTTOM":
                self.position = "RIGHT"
            case "TOP":
                self.position = "LEFT"

    def set_appearance(self, type_="BOTH"):
        """
        change appearance type of box
        """
        for box in self:
            box =  box.get_last_child().get_last_child()
            image = box.get_first_child()
            label = box.get_last_child()

            match type_:
                case "BOTH":
                    image.set_visible(True)
                    label.set_visible(True)

                case "TEXT":
                    image.set_visible(False)
                    label.set_visible(True)

                case "IMAGE":
                    image.set_visible(True)
                    label.set_visible(False)

        self.appearance = type_
