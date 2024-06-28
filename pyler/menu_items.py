# -*- coding: utf-8 -*-
"""
Creaete Menuitems and define actions
"""
import os

from gi.repository import Gtk as gtk
from gi.repository import GtkSource as edit
from gi.repository import GLib

from tercihler import ConfigWindow
from buildtool import ToolItem

from custom_button import(
    MakeHamburger, ToolBar
)

from shortcut import ShowShortCuts

from araclar import (
    TMP_FILE, MENUSETUP,
    ICONS, LANGS,
    get_stock, hakkinda
)

DEFAULT = "../templates/default.css"
MAIN = "../templates/main.css"
STYLE_SCHEME = edit.StyleSchemeManager()
SCHEME_IDS = STYLE_SCHEME.get_scheme_ids()

GLIB_TRUE = GLib.Variant.new_boolean(True)
GLIB_FALSE = GLib.Variant.new_boolean(False)

class MenuItems():
    """"
    it should have two propery class that return
    toolbar and hide widgets
    """
    def __init__( self, wiki_editor):
        """"
        new_but should  be defined in self
        """
        self.wiki_editor = wiki_editor
        self.operations = wiki_editor.operations
        self.gl_b = wiki_editor.gl_b

        self.toolbar = ToolBar()
        self.gl_b.update({"tool_active": self.toolbar})

        self.menu_items = {

        "wiki_editor" : [

            ("New", lambda *_: self.new_but.emit("clicked"),
            "<primary>N" ),

            ("Open",
            lambda *x: self.operations.open_file(x),
            "<primary>O"
            ),

            ( "Save", self.operations.kayit, "<primary>S" ),
            ( "Save As", lambda *_: self.operations.kayit(save_as=True),
               "<primary><shift>S"
            ),

            ( "Find", lambda *_:
              self.wiki_editor.notebook.get_nth_page(
                  self.wiki_editor.gl_b["tab_n_page"])\
                    .arama( self.wiki_editor),
              "<primary>F"
            ),
            ( "Replace", lambda *_:
              self.wiki_editor.notebook.get_nth_page(
                  self.wiki_editor.gl_b["tab_n_page"])\
                    .arama( self.wiki_editor, replace=True),
              "<primary>H"
            ),

            ( "Print", lambda *_:
                self.wiki_editor.notebook.get_nth_page( #get current wikitext from notebook
                    self.gl_b["tab_n_page"]
                ).yazdir( data=self.gl_b["yol"], window=self.wiki_editor ) ,
              "<primary>Y"
            ),

            ("Preferences",
            lambda *_: ConfigWindow( self.wiki_editor).show_config,
            "<primary>P"
            ),
        ],

        "Toolbar Appearance": [
            ( "Only icon",
             lambda *_: self.set_toolbar(*_, type_="IMAGE"),
             "<alt>1", True ),
            ( "Only text",
             lambda *_: self.set_toolbar(*_, type_="TEXT"),
             "<alt>2", True),
            ( "Both text and icon", self.set_toolbar,
             "<alt>3", True ),
            ("Show/Hide ToolBar", self.show_hide_toolbar, "F3", True),
        ],

        "Toolbar Position": [
            ( "Left",
             self.position_tool, "<primary>3", True),
            ( "Right",
             self.position_tool, "<primary>4", True),
            ( "Top",
             self.position_tool, "<primary>1", True),
            ( "Bottom",
             self.position_tool, "<primary>2", True),
        ],

        "more_wiki": [
            ( "Show/Hide Preview", self.show_preview,  "<super>E", True),
            ( "Full Screen", self.set_fullscreen, "F11", True ),
            #if there are 4 item last item for check option
            ("Wiki Editor Css", self.set_css,  "F1", True),
        ]
        }

        for key, val in MENUSETUP["ARACLAR"].items():
            each = ( key, self.set_tool_edit, val[1] )
            index_ = list(MENUSETUP["ARACLAR"]).index(key)
            self.menu_items["more_wiki"].insert( index_, each)

        self.hamburgers = [
            MakeHamburger( self.wiki_editor, icon="applications-other"),
            MakeHamburger( self.wiki_editor, label="Düz Metin"),
            MakeHamburger( self.wiki_editor)
        ]

        self.wiki_editor.hamburgers = self.hamburgers #

        self.wiki_editor.headerbar.pack_start( self.hamburgers[0])
        self.new_but = gtk.Button(child=get_stock("document-new-symbolic") )
        self.new_but.connect("clicked",lambda *_: self.operations.yeni(False) )
        self.wiki_editor.headerbar.pack_start( self.new_but )

        self.wiki_editor.center_box.append( self.hamburgers[1])

#################################################################

        self.append_to_menu("wiki_editor")
        sub = self.append_to_menu("Toolbar Appearance", sub="Toolbar Options")

        self.append_to_menu("Toolbar Appearance", sub=sub)
        self.append_to_menu("Toolbar Position", sub="Toolbar Position")

        self.append_themes()
        self.append_languages()
        self.append_morewiki()

        self.hamburgers[0].add_to_menu("Shortucts", lambda *_:
            ShowShortCuts( self.menu_items, ICONS.items(), app=self.wiki_editor)
        )

        self.hamburgers[0].add_to_menu("About" , lambda *_: hakkinda(app=self.wiki_editor) )

        for item, list_info in ICONS.items():
            ToolItem( self.wiki_editor, item, *list_info )

    def check_state(self, *args):
        """
        chekc state whether if it's 
        a call from tercihler or ui.
        ...
        """
        action, state, group, func = args

        if state is None:
        #   print("this call from ui")
            self.update_db(action)
            for name in group:
                if action.get_name() != name:
                    name = self.wiki_editor.lookup_action(name)
                    name.set_state(GLIB_TRUE)
                    self.update_db(name)
            return False

        if state == GLIB_TRUE:
    #    print("this call from tercihler.py")
            action.set_state(GLIB_TRUE)
            func()
            action.set_enabled(False)

        return True

    def position_tool(self, action, state):
        """
        change toolbar position on screen
        options
        """
        group = [ each.title() for each in self.toolbar.options]

        direction =  action.get_name().upper()

        if self.check_state( action, state, group,
            lambda:self.toolbar.set_position(direction) ):
            return False

        if direction != self.toolbar.position:
            self.toolbar.set_position(direction)

        for position in self.toolbar.options:
            in_action = self.wiki_editor.lookup_action(position.title())
            if position == self.toolbar.position:
                in_action.set_state(GLIB_TRUE)
                in_action.set_enabled(False)
            else:
                in_action.set_state(GLIB_FALSE)
                in_action.set_enabled(True)

        return True

    def set_toolbar(self, action, state, type_="BOTH"):
        """
        set toolbar position
        and update db
        """
        actions = ["Both text and icon", "Only text", "Only icon"]
        actions = [ each.replace(" ","__") for each in actions]

        if self.check_state( action, state, actions,
            lambda: self.toolbar.set_appearance(type_) ):
            return False

        if type_ != self.toolbar.appearance:
            self.toolbar.set_appearance(type_)

        for name in actions:
            if action.get_name() == name:
                action.set_state(GLIB_TRUE)
                action.set_enabled(False)
                continue

            name_ = self.wiki_editor.lookup_action(name)
            name_.set_state(GLIB_FALSE)
            name_.set_enabled(True)

        return True

    def set_for_all(self, func):
        """
        apply settings for all opened
        notebooks...
        """
        i = -1
        current_tab = self.gl_b["tab_n_page"]
        while i < self.wiki_editor.notebook.get_n_pages():
            i +=1
            if self.wiki_editor.notebook.get_n_pages() <= 0:
                break

            self.wiki_editor.notebook.set_current_page(i)
            func()

        self.wiki_editor.notebook.set_current_page(current_tab)

    def update_db(self, action):
        """
        update data base
        ...
        """
        if action.get_state() == GLIB_TRUE:
            state = GLIB_FALSE
        else:
            state = GLIB_TRUE

        ConfigWindow( self.wiki_editor).update_setting(
            action.get_name(), state, state )

    #    action.emit("activate", action.get_state() )

    def append_to_menu(self, menu_items, sub=None):
        """
        add actions to menu
        """
        if sub is not None:
            if sub == "Toolbar Options":
                sub = self.hamburgers[0].to_sub_menu(sub)
                return sub

            sub = self.hamburgers[0].to_sub_menu(sub)

        for items in  self.menu_items[menu_items]:
            if len(items) == 4:
                self.hamburgers[0].add_to_menu(*items[0:3], check=True, sub=sub)
                continue
            self.hamburgers[0].add_to_menu(*items, sub=sub)

        return sub

    def append_languages(self):
        """
        change type of language styling for editor
        """
        def select_language(w, _):

            lang_name = LANGS[ w.get_name().replace("__"," ") ]

            lang = self.gl_b["lang_manager"].\
                guess_language( content_type=lang_name )

            self.wiki_editor.current_buffer.set_language(lang)
            self.hamburgers[1].set_label(f"{w.get_name()}")

        for language in LANGS:
            self.hamburgers[1].add_to_menu(language, select_language)

    def append_morewiki(self):
        """
        append additional menu_button
        """
        new_but = MakeHamburger( self.wiki_editor, icon="open-menu-symbolic")
        for items in  self.menu_items["more_wiki"]:
            if True in items:
                new_but.add_to_menu(*items[0:3], check=True)
                continue
            new_but.add_to_menu(*items[0:3])

        self.wiki_editor.center_box.prepend( new_but )
        new_but.add_css_class( "wiki-menu")
        new_but.set_tooltip_text("More Wiki")
     #   new_but.set_tooltip_icon_name("wiki-editor")
        self.hamburgers.append(new_but)

    def show_preview(self, widget, *_):
        """
        show/hide webkit preview
        """
        if widget.get_state() == GLIB_FALSE:
            self.wiki_editor.preview.set_visible(True)
            widget.set_state(GLIB_TRUE)
            return True

        self.wiki_editor.preview.set_visible(False)
        widget.set_state(GLIB_FALSE)
        self.wiki_editor.redkit.try_close()
        return False

    def show_grid(self, action, *_):
        """
        show grid on text editor
        """

        if action.get_state() == GLIB_FALSE:
            self.set_for_all(lambda:
                self.wiki_editor.current_editor.\
                set_background_pattern(edit.BackgroundPatternType.GRID)
            )
            action.set_state(GLIB_TRUE)
        else:
            self.set_for_all(lambda:
                self.wiki_editor.current_editor.\
                set_background_pattern(edit.BackgroundPatternType.NONE)
            )
            action.set_state(GLIB_FALSE)

        self.update_db(action)

    def append_themes(self):
        """
        append GtkSource themes into sub menu
        """
        sub = self.hamburgers[0].to_sub_menu("Themes")
        for scheme in SCHEME_IDS:
            self.hamburgers[0].add_to_menu(scheme, self.select_theme, check=True, sub=sub)

        self.hamburgers[0].add_to_menu("Show Grid", self.show_grid, "<alt>G",check=True, sub=sub)
        self.menu_items["wiki_editor"].append(["Show Grid", self.show_grid, "<alt>G"])

    def select_theme(self, widget, theme="classic"):
        """
        select theme by name
        """

        if widget.get_enabled():
            scheme = STYLE_SCHEME.get_scheme(widget.get_name() )
            widget.set_enabled(False)
            widget.set_state(GLIB_TRUE)

            for i in SCHEME_IDS:
                action = self.wiki_editor.lookup_action(i)
                if i != widget.get_name():
                    action.set_enabled(True)
                    action.set_state(GLIB_FALSE)

        else:
            scheme = STYLE_SCHEME.get_scheme( theme)
            widget.set_enabled(True)

        self.set_for_all(lambda:
            self.wiki_editor.current_buffer.set_style_scheme(scheme)
        )

        self.gl_b.update( {"selected-theme":widget.get_name() } )

        ConfigWindow(self.wiki_editor).update_setting("selected_theme",
           self.gl_b["selected-theme"], self.gl_b["selected-theme"] )

    def set_css(self, action, *_):
        """
        switch between main.css and defautl csss
        """
        add_custom_styling = self.wiki_editor.add_custom_styling

        if action.get_state() == GLIB_FALSE:
            add_custom_styling( css=MAIN)
            add_custom_styling( self.wiki_editor)
            action.set_state(GLIB_TRUE)
            self.wiki_editor.app.\
                style_manager.set_property("color-scheme", 3)

        else:
            add_custom_styling(css=DEFAULT)
            add_custom_styling( self.wiki_editor)
            action.set_state(GLIB_FALSE)
            self.wiki_editor.app.\
                style_manager.set_property("color-scheme", 0)

        self.update_db(action)


    def show_hide_toolbar(self, action, *_):
        """
        shows or hides toolbar
        """
        if action.get_state() == GLIB_FALSE:
            self.toolbar.scroll.set_visible(True)
            action.set_state(GLIB_TRUE)

        else:
            self.toolbar.scroll.set_visible(False)
            action.set_state(GLIB_FALSE)

        self.update_db(action)

    def set_fullscreen(self, widget, *_):
        """
        Set fullscreen to unfullscreen
        ...
        """
        self.gl_b.update( {"full_screen": not self.gl_b["full_screen"] } )
        if self.gl_b["full_screen"]:
            GLib.idle_add(self.wiki_editor.fullscreen)
            widget.set_state(GLIB_TRUE)
        else:
            GLib.idle_add(self.wiki_editor.unfullscreen)
            widget.set_state(GLIB_FALSE)

    def set_tool_edit(self, widget, komut=None):
        """
        activate menu item actions on click 
        """
#####  set up text using sed regex
        name = widget.get_name().replace("__"," ")
        komut = MENUSETUP["ARACLAR"][name][0]

        if konu:= self.wiki_editor.get_konu():

            with open(TMP_FILE, "w", encoding="utf-8") as dosya:
                dosya.write(konu)

            os.system(komut)

            with open(TMP_FILE, "r", encoding="utf-8") as dosya:
                self.wiki_editor.set_text(dosya.read(), color="#e92a63")

            os.system(f"rm -rf {TMP_FILE}" )
