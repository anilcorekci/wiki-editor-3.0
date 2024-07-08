# -*- coding: utf-8 -*-
"""
build and open preferences
"""
import os
import sqlite3
from ast import literal_eval
from json import loads as to_dict

from gi.repository import Adw
from gi.repository import Gtk as gtk
from gi.repository import Pango as pango
from gi.repository import GtkSource as edit
from gi.repository import GLib

WIKI_DB = os.environ['HOME']+"/.wiki_editor.db"
STYLE_SCHEME = edit.StyleSchemeManager()
SCHEME_IDS = STYLE_SCHEME.get_scheme_ids()

GLIB_TRUE = GLib.Variant.new_boolean(True)
GLIB_FALSE = GLib.Variant.new_boolean(False)


WRAP = {
    1:["WORD", None, False],
    2:["CHAR",None, True],
    3:["NONE",None, False]
}

DEFAULT = """
textview.view {
    font-family: unset;
    font-size: unset;
    font-style: unset;
    font-weight: unset;
}
"""

SET = {
    "font_spin": None, #spin button for tab indent
    "yazi": None, #gtk fontbutton for tercihler window
    "show_number":None, #show number for wikitext
    "modify_font":None,
    "yazitipi": None, # current font preference
    "font_data": DEFAULT,
}

class ConfigWindow(gtk.Window):
    """
    Build toplevel window
    """
    style = ["normal","oblique", "italic"]
    css_provider = gtk.CssProvider()
    expander = None
    expanders = []
    group = None

    def __init__(self, wikieditor):
        gtk.Window.__init__(self)

        self.notebook = wikieditor.notebook
        self.wikieditor = wikieditor
        self.wiki = wikieditor.current_editor
        self.gl_b = wikieditor.gl_b

    @property
    def show_config(self, *_):
        """
        Show configuration window
        """
        self.set_title("Wiki Editor Preferences")

        headerbar = gtk.HeaderBar()
        self.set_titlebar(headerbar)

        self.set_modal(True)

        self.connect("close-request", lambda x:
            [ x.destroy()  , self.set_ayar(request=True) ] )

        SET["font_spin"] = gtk.SpinButton()
        SET["font_spin"].props.adjustment =\
            gtk.Adjustment.new(4.0, 4.0, 32.0, 4.0, 4.0, 0.0)

        SET["font_spin"].connect("value_changed",  lambda x:
            self.wiki.set_tab_width( float( x.get_value() ) ) )

        SET["yazi"] = gtk.FontDialogButton()

        dialog = gtk.FontDialog()
        SET["yazi"].props.dialog = dialog
        SET["yazi"].connect("notify", lambda *_:  self.add_css()  )

        SET["show_number"] = self.make_switch(
            "Show line numbers",
            lambda *x:
            self.wiki.set_show_line_numbers( x[0].get_active() )
        )

        SET["for_coding"] = self.make_switch(
            "A set of configurations for coding",
            lambda *x:
            self.wiki.get_parent().for_coding( x[0].get_active() )
        )

        SET["space_drawer"] = self.make_switch(
            "Space drawer for inside text and trailing lines",
            lambda *x:
            self.wiki.get_parent().space_drawer( x[0].get_active() )
        )

        SET["space_instead_of_tab"] = self.make_switch(
            "insert spaces instead of tabs".title(),
            lambda *x:
            self.wiki.set_insert_spaces_instead_of_tabs( x[0].get_active() ))

        SET["modify_font"] = self.make_switch("Nullify font type", self.set_font)

        self.apply_setup()

    #gtk.ListBox with append method can be used instead
    #with gtk.ListBoxRow
    # see https://docs.gtk.org/gtk4/ctor.ListBoxRow.new.html
        self.group = Adw.PreferencesGroup()
      #  group.set_title("Wiki Editor 3")
       # group.set_description("Wiki Editor 3 ayarları")

        self.group.props.margin_bottom = 32
        self.group.props.margin_top = 6
        self.group.props.margin_start = 32
        self.group.props.margin_end = 36

        self.make_info_row("Set tab width")

        for widget in SET.values():
            if not widget or isinstance(widget, str):
                continue

            info = str(widget).lower()

            match info:
                case info if "pango" in info:
                    continue

                case info if "font" in info:
                    self.make_info_row("Change font type",
                        "Change font that used by wiki text")
                    self.make_row(widget)
                    self.make_info_row("Wiki Text Preferences",
                        "Settings for wiki text and spaces")
                    continue

            self.make_row(widget)

        self.make_info_row("Text Wrap Options",
            "Set textwrap type ")

        for widget in WRAP.values():
            self.make_row(widget[1], margin=72, padding=12)

        self.set_child(gtk.ScrolledWindow(child=self.group))
     #   self.get_child().set_propagate_natural_height(400)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_size_request(600, 420)

        self.set_transient_for(self.wikieditor)
        self.wikieditor.add_custom_styling(self)

        self.present()

    def make_switch(self, label, function=None):
        """
        make_switch
        """
        switch = Adw.SwitchRow()
        switch.set_title(label)

        switch.connect("activate", function)
        switch.connect("notify", function)

        return switch

    def make_info_row(self, text, sub_text=""):
        """
        builds an info row
        """

        self.expander = Adw.ExpanderRow()
        self.expander.set_title(f"<big><b>{text}</b></big>")
        self.expander.set_subtitle(sub_text)
        self.expander.set_expanded(False)

        #self.expander.set_show_enable_switch(expand)
       # self.expander.set_enable_expansion(expand)

        def hide_others(widget, *_):
            """
            set_visible...
            """
            if  widget.get_expanded():
                for expander in self.expanders:
                    if expander != widget:
                        expander.get_parent().set_visible(False)
            else:
                for expander in self.expanders:
                    expander.get_parent().set_visible(True)

        self.expander.connect("notify", hide_others)
        self.expanders.append(self.expander)
        self.make_row(self.expander, padding=12, size=42)

    def make_row(self, widget, margin=18, padding=16, size=36):
        """
        append given widget into
        preference row
        ...
        """
        row = Adw.PreferencesRow()
        row.set_child(widget)
        row.set_valign(gtk.Align.FILL)
        row.set_size_request(size, size)
        row.set_margin_bottom(padding)
        row.set_margin_top(padding)
        row.set_margin_start(margin)
        row.set_margin_end(margin)
        row.set_halign(gtk.Align.FILL)
        row.set_title_selectable(False)

        if self.expander and self.expander != widget:
            self.expander.add_row(row)
        else:
            self.group.add(row)

    def add_css(self, default=None, data=None):
        """
        sent font with css input
        ..
        """
        context = self.wiki.get_style_context()

        if default:
            self.css_provider.load_from_string(DEFAULT)
            context.add_provider(
                self.css_provider, gtk.STYLE_PROVIDER_PRIORITY_USER)
            return False

        if data:
            self.css_provider.load_from_data(data)
            context.add_provider(
                self.css_provider, gtk.STYLE_PROVIDER_PRIORITY_USER)
            return False

        font_desc = SET["yazi"].get_font_desc()
        family = font_desc.get_family()
        size_ = str( font_desc.get_size() ) [0:2]
        style = self.style[ int( font_desc.get_style() ) ]
        weight = int( font_desc.get_weight() )

        data = f"textview.view {{\
                font-family: {family};\
                font-size: {size_}pt;\
                font-style: {style}; \
                font-weight: {weight};\
            }}"

        self.css_provider.load_from_data(data)
        SET["font_data"] = data

        context.add_provider( self.css_provider,
            gtk.STYLE_PROVIDER_PRIORITY_USER )

        return True

    def radio_wrap(self, widget):
        """
        adjust wrap_mode for wikitext
        """
        value = []
        for item in WRAP.values():
            item[2] = False
            try:
                if item[1].get_active() and item[1] != widget:
                    #set checkbutton active status as False.
                    item[1].set_active(False)
            except AttributeError:
                break

            if item[1].get_active():
                self.wiki.set_wrap_mode(
                    getattr(gtk.WrapMode, item[0]) )
                item[2]  = True
            value.append(item[2])

        if True not in value:
            # then set the clicked widget's value as True
            widget.set_active(True)

        del value

    def set_font(self, *_):
        """
        set font for wikitext
        """
        if SET["modify_font"] and SET["modify_font"].get_active():
            self.add_css(True)
        else:
            SET["yazitipi"] = SET["yazi"].get_font_desc()#?
            self.add_css()

    def apply_setup(self):
        """
        applies setups to config window
        ...
        """
        data = self.set_ayar(True)
        data = {key: list_[0] for key, list_ in  data.items() }

        SET["font_spin"].props.value =  float( data["sekme"] )
        SET["for_coding"].props.active = literal_eval( data["for_coding"] )
        SET["space_drawer"].props.active = literal_eval( data["space_drawer"] )

        SET["modify_font"].props.active = literal_eval(data["yazi_tipi"])
        SET["show_number"].props.active = literal_eval(data["sekmeleri_say"] )
        SET["space_instead_of_tab"].props.active =\
            literal_eval ( data["space_instead_of_tab"] )

        ##############
        for item in WRAP.values():
            item[1] = gtk.CheckButton(label=item[0].title())
            item[1].connect("toggled", self.radio_wrap)
            item[2] = False

            if item[0] == data["wrap_mode"]:
                item[1].set_active(True)
        ##########

        font = data["font"]
        # parsing css data into dictionary...
        dialog =  SET["yazi"].get_dialog()

        font = font.replace("textview.view","")\
            .replace(";",'",').replace("    ",'"')\
            .replace(":",'":"').replace('""""','"')\
            .replace(',"""}','}').replace("\n",'')\
            .replace(",}","}").replace("' ",'"')\
            .replace('" ',' "')

        font_data = to_dict(font)

        font = pango.FontDescription.new()
        font.set_family(font_data["font-family"])
        font.set_weight(font_data["font-weight"])
        #1 pango scale eq to 1024 #...
        font.set_size(int(font_data["font-size"].replace("pt","") ) * 1024 )
        del font_data
        # see for details
        #https://docs.gtk.org/Pango/enum.Weight.html

        SET["yazi"].set_font_desc(font)
        dialog.props.language = pango.Language.from_string(font.to_string() )

    def get_setup(self):
        """
        apply settigs from wiki_db
        ..
        """
        data = self.set_ayar(True)

        self.wiki = self.wikieditor.current_editor

        for settings in sorted(data):
            set_value_as, set_value = data[settings]

            match settings:
                case "wrap_mode":
                    getattr(self.wiki, set_value) \
                        (getattr(gtk.WrapMode, set_value_as))

                case "font":
                    self.add_css(data=set_value_as)

                case "yazi_tipi":
                    if literal_eval(set_value_as) is True:
                        self.add_css(True)

                case "sekme":
                    getattr(self.wiki, set_value) \
                        ( float(set_value_as))

                case "space_drawer":
                    getattr(self.wiki.get_parent(), set_value) \
                        ( literal_eval(set_value_as) )

                case "for_coding":
                    getattr(self.wiki.get_parent(), set_value) \
                        ( literal_eval(set_value_as) )

                case "selected_theme":
                    scheme = STYLE_SCHEME.get_scheme( set_value_as.replace(" ",""))
                    self.wikieditor.current_buffer.set_style_scheme(scheme)
                    self.gl_b.update({"selected-theme": set_value_as})
                    action = self.wikieditor.lookup_action(set_value_as)
                    action.set_state(GLIB_TRUE)
                    action.set_enabled(False)

                case settings if settings in self.wikieditor.list_actions():

                    if self.wikieditor.notebook.get_n_pages() > 1:
                        match settings:
                            case "Show__Grid":
                                pass
                            case _:
                                continue

                    action = self.wikieditor.lookup_action(settings)
                    set_value = literal_eval(set_value.title())

                    if set_value:
                        action.set_state(GLIB_TRUE)
                        action.emit("activate", GLIB_TRUE)
                    else:
                        action.set_state(GLIB_FALSE)
                        action.emit("activate", GLIB_FALSE)

                case _:
                    getattr(self.wiki, set_value) \
                        ( literal_eval(set_value_as) )

    def update_setting(self, preference, set_value, set_value_as):
        """
        update given preference
        """
        con = sqlite3.connect(WIKI_DB)
        cur = con.cursor()
        cur.execute(
            f"UPDATE settings SET value='{set_value}|{set_value_as}'" +
            f"WHERE preference='{preference}'"
        )

        con.commit()

    def set_ayar(self, data=False, set_up=False, request=None):
        """
        write configs to wiki.db
        """
        if not os.path.isfile(WIKI_DB):
            os.system(f"cp wiki_editor.db {WIKI_DB}")

        con = sqlite3.connect(WIKI_DB)
        cur = con.cursor()

# Retrun sql data as a dictionary##
        if data is not False:
            cur.execute('SELECT preference, value FROM settings')
            ans = dict(cur.fetchall()) #; print(ans)
            #split "|" and convert key item as a list
            return {key: ans[key].split("|") for key in ans}

#############################################
        # set_up ui data from wiki.db
        if set_up is True:
            self.get_setup()
            return False

        ###### update data from ui input ###############

        data = {
            "sekme": [
                f"{ SET['font_spin'].get_value() }",
                "set_tab_width"
                ],

            "font": [
                SET["font_data"] ,
                "modify_font"
                ],

            "selected_theme": [
                self.wikieditor.gl_b["selected-theme"],
                self.wikieditor.gl_b["selected-theme"],
            ],

            "yazi_tipi": [
                f"{ SET['modify_font'].get_active() }",
                "modify_font"
                ],

            "sekmeleri_say": [
                f"{ SET['show_number'].get_active() }",
                "set_show_line_numbers"
                ],

            "space_instead_of_tab": [
                f"{ SET['space_instead_of_tab'].get_active() }",
                "set_insert_spaces_instead_of_tabs"
                ],

            "for_coding": [
                f"{ SET['for_coding'].get_active() }",
                "for_coding"
                ],

            "space_drawer": [
                f"{ SET['space_drawer'].get_active() }",
                "space_drawer"
                ],

            "wrap_mode": [
                [ wrap_[0] for wrap_ in WRAP.values() if wrap_[2] ] [0],
                'set_wrap_mode'
                ],
            }

        # Write the data in wiki-editor.db file

        for preference, list_  in data.items():
            self.update_setting(preference, *list_)

        if request:
            i = -1
            current_tab = self.gl_b["tab_n_page"]
            while i < self.wikieditor.notebook.get_n_pages():
                i +=1
                if self.wikieditor.notebook.get_n_pages() <= 0:
                    break

                self.wikieditor.notebook.set_current_page(i)
                self.get_setup()

            self.wikieditor.notebook.set_current_page(current_tab)
            return False

        self.set_ayar(set_up=True)
        return True
