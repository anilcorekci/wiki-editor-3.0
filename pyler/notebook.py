# -*- coding: utf-8 -*-
#pylint:disable=C0413, R0902
"""
Wiki Editor 2010!
"""
import os
import re
import time

from threading import Timer
from threading import Thread

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GtkSource', '5')

from gi.repository import Gtk as gtk
from gi.repository import GtkSource as edit
from gi.repository import GLib
from gi.repository import Gdk as gdk


from file_operations import FileOperation
from menu_items import MenuItems
from set_text import SetText
from araclar import mesaj_button
from redkit import Redkit
#from terminal import Terminal

UNDEFINED = "New Document"
STYLE_SCHEME = edit.StyleSchemeManager()
SCHEME_IDS = STYLE_SCHEME.get_scheme_ids()

DEFAULT = "../templates/default.css"
MAIN = "../templates/main.css"
WAIT = gdk.Cursor.new_from_name("wait")
DEFAULT_TEXT = gdk.Cursor.new_from_name("text")

#TODOD.. HAVE A LOOK AT DND DRAG AND DROP EXAMPLE
#NOT NEEDED LOOK FOR MULTIPLE FILE OPEN OPTION
#DONE CREATE SETTINGS WINDOW TO MODIFY TOOLBAR AND SHORTCUTS
#TODOD CREATE ANOTHER TEMPLATES DIRECTORY FOR OTHER WIKI PAGES..

class WikiEditor(gtk.ApplicationWindow):
    """
    Kullanılan genel değişkenlerin listesi
    """
    css_provider = gtk.CssProvider()
    hamburgers = [] # defined by menu_items.py
    horizontal = None # hbox for toolbar
    size = 0 # responsive margin bottom size for textview
    gl_b = {
        "tab_n_page": None, # current nth page of notebook
        "yol": "/file//path", # file path of wikitext
        "name": "str", # file name of wikitext
        "tool_active": None, # gtk.Toolbar,
        "full_screen": None, #top_level window value
        "scroll-flag":None,
        "lang_manager":  edit.LanguageManager(),
        "selected-theme": None,
        "overlay":None,
        "progress":None,
    }

    def __init__(self, app):
        """
        Menu and widget build on gtk window
        add window actions and tools
        """
        gtk.ApplicationWindow.__init__(self, application=app)
        self.app = self.get_application()

        self.connect("close-request", self.soru)
        self.connect("state-flags-changed", self.responsive_margin )
     #   self.set_title(" Wiki Editor 3" )


        display = self.get_display()
        itheme = gtk.IconTheme.get_for_display (display)
        itheme.add_search_path( os.environ['PWD'] )

        self.set_default_icon_name("wiki-editor")
        self.set_icon_name("wiki-editor")
        self.set_title(" Wiki Editor 3" )

        self.headerbar = gtk.HeaderBar()
        self.headerbar.set_size_request(-1, 22) #!
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_decoration_layout("menu:minimize,close")

        header_event = gtk.EventControllerMotion.new()
        self.headerbar.add_controller(header_event)

        header_event.connect("enter", lambda _,x,__:
            GLib.idle_add(self.headerbar.set_show_title_buttons,True)
            if x >= self.get_width() - 24
            else GLib.idle_add(self.headerbar.set_show_title_buttons,False)
        )
        header_event.connect("leave", lambda *_: 
            GLib.idle_add(self.headerbar.set_show_title_buttons,False)
        )

        self.set_titlebar(self.headerbar)

        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_tabs(False)

        self.notebook.connect("switch-page", self.switch)
        self.notebook.connect("change-current-page",
            lambda *_: self.current_buffer.emit("cursor-moved")
        )

        notebook_event = gtk.EventControllerScroll.new(gtk.EventControllerScrollFlags.HORIZONTAL)
        self.notebook.add_controller(notebook_event)
        notebook_event.connect("scroll", self.notebook_scroll)
        notebook_event.connect("scroll-begin",
            lambda *_: self.gl_b.update({"scroll-flag":True})
        )

        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)

        self.ileti = gtk.Label(halign=gtk.Align.START)

        self.operations = FileOperation(self)

        self.center_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.center_box.set_halign(gtk.Align.FILL)
        self.center_box.set_margin_start(12)
        self.center_box.set_margin_end(2)

        self.headerbar.pack_end(self.center_box)

        self.headerbar.set_title_widget(
            gtk.Label(label=" Wiki Editor  ",
            width_chars=6,justify=2,
            use_markup=True, ellipsize=3 )
        )
        self.title = self.headerbar.get_title_widget()
        self.title.get_layout().set_spacing(2.7*1024)

        table = gtk.Box(orientation=gtk.Orientation.VERTICAL)

        craete_menu = MenuItems(self)
        self.center_box.prepend(self.ileti)

        toolbar = craete_menu.toolbar

        self.progress = gtk.ProgressBar()

        self.horizontal = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.horizontal.append(gtk.Overlay(child=self.notebook))
        self.horizontal.prepend(toolbar.scroll)
        
        #table.append(self.webview)
        self.redkit, self.preview = Redkit(table, self.horizontal).widgets
     #   table.append(Terminal().interface)

        self.set_child(table)

        self.add_custom_styling(self)
        self.add_custom_styling(self.progress)

    def notebook_scroll(self, _, position, *__):
        """
        #args = scroll, #position,# flag=None
        Scroll Event for gtk notebook
        """
        if self.gl_b["scroll-flag"] is True:
            if position > 0:
                self.notebook.next_page()
            if position < 0:
                self.notebook.prev_page()

            self.gl_b.update({"scroll-flag":None})
            self.current_buffer.emit("cursor-moved")

#    notebook_event.connect("decelerate", lambda *_: notebook_event.emit("scroll-begin"))

    def guess_language(self, file_path):
        """
        guess and update language for menu_button
        """
        language = self.gl_b["lang_manager"].guess_language(file_path)

        try:
            lang_name = language.get_mime_types()[0]
            lang_name = re.sub(".*.-", "", lang_name)
            self.hamburgers[1].set_label(lang_name)

        except AttributeError:
            self.hamburgers[1].set_label("text/plain")

        return language

    def update_progress(self, i):
        """
        pulsate progressbar and
        set fraction from given number
        """
        self.progress.pulse()

        match i:
            case i if i > 140:
                self.progress.set_fraction(i/200)
            case i if i > 100:
                self.progress.set_fraction(i/300)
            case i if i > 70:
                self.progress.set_fraction(i/140)
            case i if i > 40:
                self.progress.set_fraction(i/180)
            case _:
                self.progress.set_fraction(i)

        return False

    def show_progress(self):
        """
        add progressbar into overlay and
        start pulsing...
        """
        if self.notebook.get_n_pages() > 1:
            self.progress.set_margin_top(46)
        else:
            self.progress.set_margin_top(0)

        if self.gl_b["progress"]:
            return False

        overlay = self.notebook.get_parent()
        self.progress.set_valign(gtk.Align.START)
        self.progress.set_halign(gtk.Align.FILL)

        self.gl_b["progress"] = True

        overlay.add_overlay(self.progress)

        def progress_target():
            """
            target for timer
            """
            for i in range(200):
                GLib.idle_add(self.update_progress, i)
                if i > 150:
                    time.sleep(0.010)
                    continue
                time.sleep(0.005)

            self.current_editor.set_cursor(DEFAULT_TEXT)
            overlay.remove_overlay(self.progress)
            self.gl_b["progress"] = False

        self.current_editor.set_cursor(WAIT)
        thread = Thread(target=progress_target)
        thread.daemon = True
        thread.start()
        return True

    def add_custom_styling(self, widget=None, css=None):
        """ iterate children recursive
        """
        if css and os.path.exists(css):
            try:
                self.css_provider.load_from_path(css)
            except TypeError as err:
                print(f"Error in loading CSS \n {err}")
                return None
            return False

        def _add_widget_styling(widget):
            context = widget.get_style_context()
            context.add_provider( self.css_provider,
                gtk.STYLE_PROVIDER_PRIORITY_USER )

        _add_widget_styling(widget)
        for child in widget:
            self.add_custom_styling(child)

        return True

    def switch(self, tab=False, widget= False, tab_n_page=False):
        """print(widget, tab_n_page)
        check file_path and assing to self.gl_b["yol"]
        ## hbox = tab.get_tab_label(widget)
           label = hbox.get_first_child()
        """

        label = tab.get_tab_label(widget).get_center_widget()
        file_path = label.get_tooltip_text()

        self.gl_b["tab_n_page"] = tab_n_page
        self.gl_b["name"] = label.get_text()

        if ":" in self.gl_b["name"] :
            #if basename contain the seperator ':'
            file_path =  re.sub(r'^([^:]*):', "", file_path )
            #remove before first appearance..
            self.gl_b["yol"] = file_path
        else:
            self.gl_b["yol"] = file_path.split(":")[1]

        #removes leading spaces..
        self.gl_b["yol"] = re.sub(r"^\s+", "", self.gl_b["yol"])

        if not os.path.isfile(self.gl_b["yol"]):
            self.gl_b["yol"] = f"{UNDEFINED} : {tab_n_page + 1}"
            self.title.set_markup("<span size='11776'>"
            f"<b>{self.gl_b["name"]}</b></span>")

        else:
            #remove basename from path
            cute_title = re.sub(self.gl_b["name"]+"$","", self.gl_b["yol"])
            if os.environ["HOME"] in cute_title:
                #replace home path to ~
                cute_title = cute_title.replace(os.environ["HOME"],"~")
                cute_title = re.sub("/$","", cute_title)

            self.title.set_markup("<span size='11776'>"
            f"<b>{self.gl_b["name"]}</b></span>\n"
            "<span size='11064' weight='370'><small>"
            f'{cute_title}'
            "</small></span>")

        self.title.set_tooltip_text(label.get_tooltip_text())
        self.guess_language(label.get_tooltip_text())
        #call after signal ended!
        def get_numbers():
            """
            emit cursor to update ileti
            ....
            with timer the function happens after 
            this is a fix for updating current buffer..
            #hint: see line numbers update without it.
            """
            try:
                self.current_buffer.emit("cursor-moved")
            except AttributeError:
                pass

        t = Timer(.001, get_numbers) #<3
        t.start()

    @property
    def current_editor(self):
        """
        return current editor
        """
        page = self.notebook.get_current_page()
        scroll_w = self.notebook.get_nth_page(page)

        try:
            buffer = scroll_w.get_widget()
            buffer.set_left_margin(8)
        except AttributeError:
            return None

        return buffer

    @property
    def current_buffer(self):
        """
        return current buffer
        """
        return self.current_editor.get_buffer()

    def set_text(self, *args, **kwargs):
        """
        set current buffer text
        """
        SetText(self.current_buffer, *args, **kwargs)

    def responsive_margin(self, *flags):
        """
        ...margin bottom allocation for textview
        get_allocation #https://docs.gtk.org/gdk4/struct.Rectangle.html#description
        """
        try:
            height = self.current_editor.get_visible_rect().height
        except AttributeError:
            return False

        if height < 150 or gtk.StateFlags.PRELIGHT in flags:
            return False

        iter_ = self.current_buffer.get_end_iter()
        location = self.current_editor.get_iter_location(iter_).height

        if self.size == [ (height - location), self.current_editor ]:
            return False

        GLib.idle_add(
            self.current_editor.set_bottom_margin,
            height - location
        )

        self.size = [ ( height - location ), self.current_editor ]
        return True

    def get_konu(self, all_text=False):
        """
        return selection of text
        """
        if all_text is True:
            start, end = self.current_buffer.get_bounds()
            konu = self.current_buffer.get_slice(start, end,1)
            return konu

        if bounds:=self.current_buffer.get_selection_bounds():
            start, end = bounds
            konu = self.current_buffer.get_slice(start, end,1)
            return konu

        self.ileti.set_text("No selected text!")
        return False

    def soru(self, *_):
        """
        ask and close toplevel window
        """
        if self.gl_b["overlay"]:
            self.gl_b["overlay"].unrealize()

        i = -1
        while True:
            i += 1
            self.notebook.set_current_page(i)

            if  self.notebook.get_n_pages() < i:
                self.destroy()
                return False

            elif self.current_editor:
                if self.current_buffer.get_modified():
                    soru = mesaj_button(
                    heading="<b>Unsaved changes found </b>",
                    body="<span font-weight='400'><i>"
                    "Changes which are not saved will be lost permanently. "
                    "Are you sure about quitting?</i></span>",
                    buttons=["YES:2","NO:0"] )

                    soru.set_size_request(400,-1)

                    def response(widget, response_id):
                        response_id = int( widget.choose_finish(response_id) )
                        if response_id == 0:
                            self.destroy()
                            return False
                        self.set_sensitive(True)

                    self.set_sensitive(False)
                    soru.choose(self, None, response)
             #       self.add_custom_styling(soru)
                    break

            else: 
                self.destroy()
                return False

        return True #in this way gtk.main continue
