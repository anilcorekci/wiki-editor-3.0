#!/bin/python3.12
#pylint: disable=C0413
"""
terminal emulator for wikieditor
"""
import os
import gi
gi.require_version('Vte', '3.91')

#dependency gir1.2-vte-3.91
from gi.repository import Vte
from gi.repository import GLib
from gi.repository import Gdk as gdk
from gi.repository import Gio, Gtk as gtk
from gi.repository import Pango as pango


#WIKI_LOG = "/tmp/wiki-editor.log"
GLIB_TRUE = GLib.Variant.new_boolean(True)
GLIB_FALSE = GLib.Variant.new_boolean(False)

class VTE(Vte.Terminal):
    """
    VTE build descriptions
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spawn_async(    Vte.PtyFlags.DEFAULT, # Pty Flags
            os.environ['HOME'], # Working DIR
            ["/bin/bash"], # Command/BIN (argv)
            None, # Environmental Variables (envv)
            GLib.SpawnFlags.DEFAULT, # Spawn Flags
            None, None, # Child Setup
            -1, # Timeout (-1 for indefinitely)
            None, # Cancellable
            None, # Callback
            None # User Data
        )

class Terminal(VTE):
    """
    Setting up the Terminal widget
    """
    menu = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_visible(False)
#
#       # self.connect("commit", self.to_commit)
        self.connect("setup_context_menu", self.show_menu)
        self.connect("eof", self.to_eof)

        self.set_audible_bell(True)

        bg = gdk.RGBA()
        bg.parse("@headerbar-bg-color")

        fg = gdk.RGBA()
        fg.parse("#333333")
        self.set_color_foreground(fg)
        fg.parse("#071952")
        self.set_color_cursor_foreground(fg)
        fg.parse("#088395")
        self.set_color_cursor(fg)
        self.set_colors(
            background = bg,
            foreground =fg)

        font = pango.FontDescription.new()
        font.set_family("monospace")
        font.set_weight(1000)
        font.set_size(12288)
        font.set_stretch(8)

        self.set_font(font)
        self.set_cursor_blink_mode(1)
        self.set_enable_bidi(True)
        self.set_text_blink_mode(3)
        self.set_allow_hyperlink(True)
    #    self.add_css_class("vte-terminal")

    def to_dir(self, dir_):
        """
        spawn new with given working dir_
        """
        self.spawn_async( Vte.PtyFlags.DEFAULT, dir_,
            ["/bin/bash"], None, GLib.SpawnFlags.DEFAULT,
            None, None,  -1, None, None,  None
        )

    def add_action(self, window):
        """
        build new menu model
        """
        menu = Gio.Menu.new()
        self.set_context_menu_model(menu)

        def action_connect(action_, funk, key_=None):
            accel_name = action_.replace(" ","_")
            menu.append(f"{action_}", f"win.{accel_name}")
            action = Gio.SimpleAction.new(f"{accel_name}", None)
            self.menu[action_] = action
            action.connect("activate",funk)
            window.add_action(action)

            if key_:
                window.app.set_accels_for_action( f"win.{accel_name}", [key_] )

        action_connect("Select All",
            lambda *_: self.select_all(),
            key_="<ctrl><shift>A"
        )

        action_connect("Set Background", self.set_color_on_select )
        action_connect("Set Foreground",
            lambda *_: self.set_color_on_select(foreground=True)
        )

        action_connect("Copy", lambda *_:
            self.copy_clipboard_format(Vte.Format.TEXT),
            "<ctrl><shift>C"
        )

        action_connect("Insert Text", lambda *_:
           [self.copy_clipboard_format(Vte.Format.TEXT),
            window.set_text(self.get_text_selected(1), True) ]
        )

        action_connect("Insert As Html", lambda *_:
           [self.copy_clipboard_format(Vte.Format.HTML),
            window.set_text(self.get_text_selected(2), True) ]
        )

        action_connect("Paste", lambda *_:
            self.paste_clipboard(), "<ctrl><shift>V")

    def to_eof(self, *_):
        """
        destroy self on eof
        """
        self.get_parent().set_end_child(None)
        self.unrealize()
   #     self.destroy()
 #       print(args)

    def show_menu(self, *_):
        """
        set action on menu call
        """
        def set_enable(state):
            """
            set_action state
            """
            for name, action in self.menu.items():
                if not name.lower() in ("insert text","insert as html", "copy","paste"):
                    continue
                action.set_enabled(state)

        if self.get_text_selected(1):
            set_enable(True)
            return False

        set_enable(False)
        return True

    def set_color_on_select(self, *_, foreground=None):
        """
        ....
        """
        renksec = gtk.ColorChooserDialog()
        renksec.set_property('show-editor', False)
        renksec.set_title("Select a color")
        renksec.set_transient_for(self.get_root())
        renksec.set_modal(True)
        def set_color(_, response=None):
            """
            select color convert to rgba in span
            """
            if response == gtk.ResponseType.OK:
                if foreground:
                    self.set_color_foreground(renksec.get_rgba())
                else:
                    self.set_color_background(renksec.get_rgba())

            renksec.destroy()

        renksec.connect("response", set_color)
        renksec.show()
