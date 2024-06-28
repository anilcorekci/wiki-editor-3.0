# -*- coding: utf-8 -*-
#pylint: disable=C0413
"""
Search replace modify buffer
"""
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GtkSource', '5')

from gi.repository import Gtk as gtk
from gi.repository import GLib
from araclar import get_stock


class SearchBar:
    """
    applies tags, and shows overlay
    ..
    """
    renk = {} #buffer: tag
    total = -1
    case_senstivie = None
    replace = None
    ileti = None
    previous_one = None
    search_text = None

    def __init__(self, app, *_, replace=None):
        """
        build search dialog and show
        """
        self.ileti = app.ileti

        if app.gl_b["overlay"]:
            overlay = app.notebook.get_parent()
            overlay.remove_overlay(app.gl_b["overlay"])
            app.gl_b["overlay"].unrealize()

        hbox2, searchbar =  self.make_below(app)
        hbox = self.make_above(hbox2, app, replace)

        if not replace:
            hbox2.set_visible(False)

        box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        box.append(hbox)
        box.append(hbox2)


        buffer = app.current_buffer
        if bounds:=buffer.get_selection_bounds():
            start, end = bounds
            konu = buffer.get_slice(start, end, None)
            self.search_text.set_text(konu)
            self.search_text.select_region(0, len(konu))

        searchbar.set_child(box)
        searchbar.connect_entry(self.search_text)

        overlay = app.notebook.get_parent()
        overlay.add_overlay(searchbar)
        self.search_text.grab_focus() #..

        if app.notebook.get_n_pages() > 1:
            searchbar.set_margin_top(46)

        app.add_custom_styling(searchbar)

        searchbar.set_show_close_button(True)
        self.search_text.connect("unmap", lambda *_: searchbar.hide() )

    def make_above(self, hbox2, app, replace):
        """
        create first box in searchbar
        and returns
        """
        search_text  =  gtk.SearchEntry()
        self.search_text = search_text
        self.search_text.set_placeholder_text("Write here")
        self.search_text.set_size_request(170 ,30)
        self.search_text.connect("activate", lambda *_: self.ara(app=app))
        self.search_text.connect("search-changed",  lambda *_: self.ara(app=app))

        image_up = self.make_button("go-up",
            lambda *_: self.search_up(app=app)
        )

        image_up.props.margin_start = 26
        image_up.props.margin_end = 7

        image_down = self.make_button("go-down",
            lambda *_: self.search_down(app=app)
        )
        image_down.props.margin_end = 2

        hbox = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)

        hbox.props.margin_top = 14
        hbox.props.margin_bottom = 14

        case_senstivie =  gtk.CheckButton(child=get_stock("tools-check-spelling-symbolic"))
        self.case_senstivie = case_senstivie
        self.case_senstivie.set_margin_start(42)
        self.case_senstivie.set_margin_end(32)

        regex = gtk.Button(child=get_stock("edit-find-replace-symbolic"))
        regex.connect("clicked", lambda _, regex_val={1: replace}:[
            regex_val.update({1: not regex_val[1]}),
            hbox2.set_visible(regex_val[1])
        ])

        regex.set_margin_end(6)

        for widget in vars().values():
            if isinstance(widget, (gtk.Box, gtk.Window)):
                continue

            if isinstance(widget, gtk.Widget):
                hbox.append(widget)

        return hbox

    def make_below(self, app):
        """
        create second box in searchbar
        and returns        
        """
        hbox2 = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        hbox2.props.margin_top = 5
        hbox2.props.margin_bottom = 14
        hbox2.props.spacing = 18

        self.replace = gtk.Entry()
        self.replace.set_size_request(210 ,25)

        replace_but = gtk.Button(label="Replace")
        replace_but.connect("clicked", lambda *_:
            self.search_down(app=app, replace=True))

        replace_all = gtk.Button(label="Replace All")
        replace_all.connect("clicked", lambda *_:
            self.ara(app=app, replace_all=True))

        hbox2.append(self.replace)
        hbox2.append(replace_but)
        hbox2.append(replace_all)

        searchbar = gtk.SearchBar()
        searchbar.set_search_mode(True)
        app.gl_b["overlay"] = searchbar

        searchbar.set_valign(gtk.Align.START)
        searchbar.set_halign(gtk.Align.END)

        return hbox2, searchbar

    def make_button(self, stock, function):
        """
        return image 
        add gesture click to image
        from given function..
        """
        image = get_stock(stock)
        image.set_margin_start(6)
        event = gtk.GestureClick.new()
        image.add_controller(event)
        event.connect("pressed", function)

        return image

    def check_tags(self, app):
        """
        define and returns
        flag, iter_, str_text, buffer
        """
        try:
            buffer = app.current_buffer
        except RecursionError:
            return False

        iter_ = buffer.get_iter_at_mark(buffer.get_insert())
        str_text = self.search_text.get_text()

        start, end = buffer.get_bounds()

        if buffer in self.renk:
            buffer.remove_tag(self.renk[buffer], start, end)
       #     del self.renk[buffer]

        self.renk[buffer] = buffer.create_tag(background="yellow",foreground="#000000")

        if self.case_senstivie.get_active():
            flag = gtk.TextSearchFlags.CASE_INSENSITIVE
        else:
            flag = gtk.TextSearchFlags.TEXT_ONLY

        return flag, iter_, str_text, buffer

    def ara(self,  *_, replace_all=False, app=None):
        """
        search backward or forward within text buffer
        """
        try:
            flag, iter_, str_text, buffer = self.check_tags(app)
        except TypeError:
            return False

        if replace_all:
            self.replace_all(buffer, str_text, flag)
            return False

        iter_ = buffer.get_start_iter()
        iter_.set_line_offset(0) #####

        i = 0
        while True:
            found = iter_.forward_search(str_text, flag)
            if not found:
                break

            i += 1
            match_start, match_end = found
            self.apply_tag(buffer, match_start, match_end)
            iter_ = match_end

        if not str_text or i < 1:
            self.ileti.set_text("No match found!")
            return False

        self.ileti.set_text(f"{i} match found.." )
        self.total = i

        if self.total == 1:
      #      print(self.total)
            app.current_editor.scroll_to_iter(
                match_start, 0.1, True, 0.0, 0.5 )

        return True

    def check_iter(self, buffer, found, forward=False, replace=None):
        """
        checking to push search..
        """
        str_text = self.search_text.get_text()

        if len(str_text) == 0:
            return False

        if not found:

            if forward:
                iter_ = buffer.get_start_iter()
                iter_.set_line_offset(0) #####

                buffer.place_cursor(iter_)

            elif not forward:
                iter_ = buffer.get_end_iter()
                buffer.place_cursor(iter_)

            # when it's eq to 0 it gives recursion error..
            if not replace and self.total >= 1:
                #print(self.total)
                # soo when eq to 1  stop it..
                if self.total == 1:
                    return False

                return True

        return False

    def apply_tag(self, buffer, match_start, match_end, color=None):
        """
        apply tag for each step
        """
        if color:
            self.renk[buffer] = buffer.create_tag(
                background=color,
                foreground="#000000"
            )

        self.previous_one = match_start, match_end
        buffer.apply_tag(self.renk[buffer], match_start, match_end)

    def search_up(self, app=None):
        """
        search_up
        """
        try:
            flag, iter_, str_text, buffer = self.check_tags(app)
        except TypeError:
            return False

        found = iter_.backward_search(str_text, flag, None)

        if not found:
            if self.check_iter(buffer, found):
                self.search_up(app=app)
            return False

        match_start, match_end = found

        if self.previous_one and match_start.in_range(*self.previous_one):
            buffer.place_cursor(match_start)
            self.search_up(app=app)
            return False

        self.apply_tag(buffer, match_start, match_end)
        buffer.select_range(match_start, match_end)

        GLib.idle_add( app.current_editor.scroll_to_mark,
            buffer.get_insert(), 0.1, True, 0.0, 0.5 )

        return True

    def search_down(self, app=None, replace=None):
        """
		continue seaching value  after or before selection
        follow after and before via get_start_iter
        # get_iter_at_mark #buffer_get_insert
        # and with buffer selection bounds and bounds
        #hint for following the functions look for 
        math cases and previous one..
        """
        try:
            flag, iter_, str_text, buffer = self.check_tags(app)
        except TypeError:
            return False

        found = iter_.forward_search(str_text, flag, None)

        if not found:
            if self.check_iter(buffer, found, forward=True, replace=replace):
                self.search_down(app=app)
            return False

        match_start, match_end = found

        if self.previous_one and match_start.in_range(*self.previous_one):
            buffer.place_cursor(match_end)
            self.search_down(app=app)
            return False

        self.apply_tag(buffer, match_start, match_end)
        buffer.select_range(match_end, match_start)

        if replace:
            self.buffer_replace(buffer, flag)

        GLib.idle_add( app.current_editor.scroll_to_mark,
            buffer.get_insert(), 0.1, True, 0.0, 0.5 )

        return True

    def replace_all(self, buffer, str_text, flag):
        """
        replace_all
        """
        iter_ =  buffer.get_end_iter() #!
        buffer.begin_user_action()
        self.renk[buffer] = buffer.create_tag(
            background="rgba(143, 240, 164, 1.0)",
            foreground="#000000")

        i=0
        while True:
            found = iter_.backward_search(str_text, flag)

            if not found or i == self.total:
                break

            i+=1
            match_start, match_end = found
            iter_ = self.buffer_replace_all(buffer, match_start, match_end)

        buffer.end_user_action()
        self.ileti.set_text(f"{i} match changed.." )
        self.total = 0 #

    def buffer_replace_all(self, buffer, match_start, match_end):
        """
        #if the mathcing word 
        #consists of more than one word
        backward_char n times of text
        else bakcward to word start
        ...
        """

        replace_text = self.replace.get_text()
        buffer.delete(match_start, match_end)
        buffer.insert(match_start, replace_text )

        # if replace_text is a list of word..
        if len(replace_text.split() ) >= 1:

            match_start.backward_char()
            start, end = match_start.copy(), match_start.copy()

            j = 0
            while j < len(replace_text) -1:
                j+=1
                start.backward_char()

            end.forward_char()

            buffer.apply_tag(self.renk[buffer], start, end)
            return match_start

        start, end = match_start.copy(), match_start.copy()

        j = 0
        while j < len(replace_text):
            j+=1
            start.backward_char()

        buffer.apply_tag(self.renk[buffer], start, end)
        return start

    def buffer_replace(self, buffer, flag):
        """
        replace and apply new tag to 
        found iter...
        """
        buffer.begin_user_action()

        buffer.remove_tag(self.renk[buffer], *self.previous_one)

        iter_ = self.previous_one[1]
        found = iter_.backward_search(self.search_text.get_text(), flag, None)

        match_start, match_end = found

     #   buffer.place_cursor(match_start)#
        buffer.place_cursor(match_end)#

        buffer.delete(match_start, match_end)
        buffer.insert_at_cursor( self.replace.get_text() )

        match_end = buffer.get_iter_at_mark(buffer.get_insert())
        start = match_end.copy()

        j = 0
        while j < len(self.replace.get_text() ):
            start.backward_char()
            j+=1

        buffer.select_range(start, match_end)
        buffer.place_cursor(match_end) #

        self.apply_tag(buffer, start, match_end, color="rgba(127, 63, 191, 0.53)")
        buffer.end_user_action()

        self.total -=1 #
