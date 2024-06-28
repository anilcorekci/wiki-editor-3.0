# -*- coding: utf-8 -*-
#pylint:disable=C0413
"""
Webkit View for Wiki-Editor
"""
import gi
gi.require_version('WebKit', '6.0')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import WebKit

from araclar import get_stock

class Redkit:
    """
    Puts Webkit view in gtk.Paned
    """
    wait = gdk.Cursor.new_from_name("wait")

    def __init__(self,table, horizontal):
        """
        append self.webview within paned
        ...
        """
        self.horizontal = horizontal
        # https://webkitgtk.org/reference/webkitgtk/stable/method.self.webview.terminate_web_process.html
        self.webview = WebKit.WebView()
        self.webview.set_size_request(250, 400)
        self.webview.connect("close", lambda view: view.terminate_web_process())

        paned = gtk.Paned()
        paned.set_orientation(gtk.Orientation.VERTICAL)
        paned.set_start_child(self.horizontal)
        paned.set_end_child(gtk.Overlay(child=self.webview))
    #    paned.set_shrink_start_child(False)

        self.preview = paned.get_end_child()
        self.preview.set_visible(False)
        table.append(paned)

        self.find_entry = gtk.Entry()
        self.find_entry.set_placeholder_text("https://")
        self.find_entry.set_text("https://")
        self.find_entry.set_size_request(400,-1)
        self.find_entry.connect("activate", lambda w:
            self.webview.load_uri(w.get_text())
        )

        self.webview.connect("resource-load-started", self.update_uri )

        self.searchbar = gtk.SearchBar()
        self.searchbar.set_search_mode(True)

        self.searchbar.set_valign(gtk.Align.START)
        self.searchbar.set_halign(gtk.Align.END)
        self.searchbar.connect_entry(self.find_entry)
        self.searchbar.props.margin_end = 8
        self.append_to_searchbar(paned)

    def append_to_searchbar(self, paned):
        """
        append buttons into searchbar
        """
        home = gtk.Button(child=get_stock("go-home-symbolic"))
        home.connect("clicked", lambda *_:
            self.webview.load_uri("https://en.wikipedia.org/w/index."
            "php?title=Wikipedia:Template_index/General&action=edit")
        )

        go_back = gtk.Button(child=get_stock("go-previous-symbolic"))
        go_back.connect("clicked", lambda *_: self.webview.go_back())

        go_forward = gtk.Button(child=get_stock("go-next-symbolic"))
        go_forward.connect("clicked", lambda *_: self.webview.go_forward())

        zoom = gtk.Button(child=get_stock("zoom-in-symbolic"))
        zoom.connect("clicked",  lambda *_:
            self.webview.set_zoom_level(self.webview.get_zoom_level() + 0.10)
        )

        zoom_o = gtk.Button(child=get_stock("zoom-out-symbolic"))
        zoom_o.connect("clicked",  lambda *_:
            self.webview.set_zoom_level(self.webview.get_zoom_level() - 0.10)
        )

        rotate = gtk.Button(child=get_stock("object-rotate-left-symbolic"))
        rotate.connect("clicked", self.rotate_view, paned )

        hide_ = {1:True}
        hide = gtk.Button(child=get_stock("sidebar-hide-symbolic"))
        hide.connect("clicked", self.hide_buttons, hide_)

        motion_control = gtk.EventControllerMotion.new()
        motion_control.connect('motion', self.motion_in, hide_ )

        self.webview.add_controller(motion_control)

        box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        box.set_spacing(12)
        box.props.margin_end = 3
        box.props.margin_start = 3
        box.props.margin_bottom = 1
        box.props.margin_top = 1

        for name, widget in vars().items():
            if isinstance( widget, (gtk.Box, gtk.Paned) ):
                continue

            if isinstance(widget, gtk.Widget):
                box.append(widget)

            if name == "go_forward":
                box.append(self.find_entry)

        self.searchbar.set_child(box)
        self.preview.add_overlay(self.searchbar)

    @property
    def widgets(self):
        """
        returns parent widgets
        """
        return self.webview, self.preview

    def motion_in(self, _, x, y, hide_): #_ event
        """
        auto hide self.searchbar when 
        sidebar-hide activated
        ... 
        """
        if hide_[1]:
            return False

        max_width = self.webview.get_width()
        max_height = self.webview.get_height()

        match self.searchbar.get_valign():
            case gtk.Align.END:
                if max_height - 200 > y :
                    self.searchbar.set_visible(False)

            case gtk.Align.START:
                if y > 200:
                    self.searchbar.set_visible(False)

        if not self.searchbar.get_visible() and x > max_width - 100:
            self.searchbar.set_visible(True)

        return True

    def rotate_view(self, buton, paned):
        """
        change paned  widget orientation
        """
        image = buton.get_child()
        if paned.get_orientation() == gtk.Orientation.VERTICAL:
            paned.set_orientation(gtk.Orientation.HORIZONTAL)
            image.set_from_icon_name("object-rotate-left-symbolic")
            self.searchbar.set_valign(gtk.Align.END)
            return True

        paned.set_orientation(gtk.Orientation.VERTICAL)
        image.set_from_icon_name("object-rotate-right-symbolic")
        self.searchbar.set_valign(gtk.Align.START)
        return False

    def hide_buttons(self,widget, hide_):
        """
        hide buttons
        """
        hide_.update({1: not hide_[1]})
        for each in widget.get_parent():
            if each == widget:
                continue
            each.set_visible(hide_[1])

        if hide_[1]:
            self.searchbar.set_margin_top(0)
        else:
            self.searchbar.set_margin_top(64)

    def update_uri(self, *_):
        """
        update entry text
        when it doesn't have grab
        ...
        """
        if self.find_entry.get_text() == self.webview.get_uri():
            return False

      #  print( self.find_entry.get_state_flags().value_names)
        flags = self.find_entry.get_state_flags().value_nicks

        if "focus-within" in flags:
            self.webview.set_cursor(self.wait)
            return False

        self.webview.set_cursor(self.wait)
        self.find_entry.set_text(self.webview.get_uri())
        return True
