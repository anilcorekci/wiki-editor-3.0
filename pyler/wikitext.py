# -*- coding: utf-8 -*-
#pylint: disable=C0413
"""
Return as a gtkScorlledWindow
contains gtkSourceView widget
"""
import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GtkSource', '5')

from gi.repository import GtkSource as edit
from gi.repository import Gtk as gtk
from gi.repository import GLib

from searchbar import SearchBar

class WikiText(gtk.ScrolledWindow):
    """
    getting variables from __main__ hito
    """
    edit = None
    seachbar = None
    tbuffer = None
    disconnect = None #!

    def __init__(self, ileti, hamburgers):
        """
        initiliaze as a scrolled window
        """
        self.ileti = ileti

        gtk.ScrolledWindow.__init__(self)
        self.set_policy(True, True)
        self.set_child(self.widget)

        menu_items = ["Wiki","Languages","Tool Items", "More Wiki"]
        menu = self.edit.get_extra_menu()

        for index_, hamburger in enumerate(hamburgers):
            if index_ < 2:
                continue
            menu.append_submenu(menu_items[index_], hamburger.menu)

    def get_widget(self):
        """
        return sourceView widget
        """
        return self.edit

    def space_drawer(self, setup=True):
        """
        Show flags for indentations and spaces
        """
        drawer = self.edit.get_space_drawer()

        if setup is not True:
            drawer.set_types_for_locations(edit.SpaceLocationFlags.ALL, edit.SpaceTypeFlags.NONE)
            return False

        drawer.set_enable_matrix(True)

        drawer.set_types_for_locations(edit.SpaceLocationFlags.LEADING,
            edit.SpaceTypeFlags.ALL)

        drawer.set_types_for_locations(edit.SpaceLocationFlags.TRAILING,
            edit.SpaceTypeFlags.SPACE | edit.SpaceTypeFlags.TAB )

        drawer.set_types_for_locations(edit.SpaceLocationFlags.INSIDE_TEXT,
            edit.SpaceTypeFlags.ALL )

        drawer.set_types_for_locations(edit.SpaceLocationFlags.NONE,
            edit.SpaceTypeFlags.NBSP)

        return True

    def for_coding(self, setup=True):
        """
        highliht brackets, use autshow flags for indent and spaceso_indent etc...
        """
        def switch_option(state):
            """ set state to given option
            """
            self.edit.set_highlight_current_line(state) #!
            self.edit.set_smart_backspace(state)
            self.edit.set_auto_indent(state)
            self.tbuffer.set_highlight_matching_brackets(state)
            self.tbuffer.set_implicit_trailing_newline(state)

        switch_option(setup)

    @property
    def widget(self):
        """
        main widget
        """
        self.tbuffer =  edit.Buffer()
        self.edit = edit.View(buffer=self.tbuffer)

        self.edit.set_bottom_margin(300) #!
        self.edit.set_top_margin(6)
        self.edit.set_left_margin(6)
        self.tbuffer.set_highlight_syntax(True)

        self.edit.set_pixels_below_lines(3)
        self.edit.set_pixels_above_lines(3)
        self.edit.set_pixels_inside_wrap(4)

        self.edit.set_input_hints(gtk.InputHints.NO_EMOJI|
            gtk.InputHints.WORD_COMPLETION| gtk.InputHints.SPELLCHECK  )

        self.edit.set_smart_home_end(edit.SmartHomeEndType.ALWAYS)

        self.tbuffer.connect("cursor-moved", self.update_cursor_position)
        self.disconnect = self.tbuffer.connect("modified-changed", self.update_tab_on_change)##!
        self.tbuffer.connect("changed", self.update_last_iter)

        self.edit.add_css_class( "wiki-editor" )

        return self.edit

    def update_tab_on_change(self, *_):
        """
        update_tab_on modify _change
        """
        app = self.get_root()
        hbox = app.notebook.get_tab_label(self)
        hbox = hbox.get_center_widget()

        if self.tbuffer.get_modified() and self.edit.get_sensitive() is True:
            if not gtk.Image in hbox:
                image = gtk.Image()#icon_name="wiki-editor-symbolic")
                image.set_pixel_size(4)
                image.set_margin_start(3)
                image.add_css_class("modified")
                app.add_custom_styling(image)
                app.notebook.emit("switch-page", self, app.gl_b["tab_n_page"])
                hbox.prepend(image)
        else:
            hbox.remove(hbox.get_first_child() )
            app.notebook.emit("switch-page", self, app.gl_b["tab_n_page"])

    def arama(self, app, *_, replace=None):
        """
        calls searchbar
        ..
        """
        self.seachbar = SearchBar( app, *_, replace=replace)

    def update_last_iter(self, *_):
        """
        update last tag position
        on change
        """
        if self.seachbar and self.seachbar.previous_one:
            self.seachbar.previous_one = None

    def update_cursor_position(self, *_):
        """
        action for search elements in text
        """
   #     tabwidth = view.get_width()
        iter_ = self.tbuffer.get_iter_at_mark(self.tbuffer.get_insert())
        row = iter_.get_line() + 1
        start = iter_.copy()
        start.set_line_offset(0)
        col = 0

        while start.compare(iter_) < 0:
           # if start.get_char() == '\t':
          #      col += tabwidth - col % tabwidth
         #   else:
            col += 1
            start.forward_char()

        GLib.idle_add(
            self.ileti.set_text,
            f'Ln: {row}, Col: {col}'
        )

    def yazdir(self, *_, data=None, window=None):
        """
        call printing dialog
        """
        compositor = edit.PrintCompositor().new_from_view(self.edit )
        compositor.set_wrap_mode(gtk.WrapMode.CHAR)
        compositor.set_highlight_syntax(True)
        compositor.set_header_format(False, 'Day  %A', None, '%F')

        filename = f"{data.split(':')[0]}"

        compositor.set_footer_format(True, '%T',
                 f"{os.path.basename(filename)}",
                 'Page %N/%Q')

        compositor.set_print_header(True)
        compositor.set_print_footer(True)

        def begin_print_cb(operation, context, compositor):
            """
			start printing action
			"""
            while not compositor.paginate(context):
                pass
            n_pages = compositor.get_n_pages()
            operation.set_n_pages(n_pages)

        def draw_page_cb(_, context, page_nr, compositor):
            """
			draw current page
			"""
            compositor.draw_page(context, page_nr)

        print_op = gtk.PrintOperation()
        print_op.connect("begin-print", begin_print_cb, compositor)
        print_op.connect("draw-page", draw_page_cb, compositor)
        res = print_op.run(gtk.PrintOperationAction.PRINT_DIALOG, window)

        if res == gtk.PrintOperationResult.ERROR:
            print ("Hatalı Baskı Dosyası:\n\n" + filename)
        elif res == gtk.PrintOperationResult.APPLY:
            print  (f'Baskı Dosyası: "{os.path.basename(filename )}"')
