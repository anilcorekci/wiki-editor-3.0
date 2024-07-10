# -*- coding: utf-8 -*-
"""
Open directory on a listview!
"""
import os
import time
import re

from  urllib import parse as PARSER
from threading import Thread
from PIL import Image

import gi

from gi.repository import Gio, GObject
from gi.repository import GLib
from gi.repository import Gdk as gdk
from gi.repository import Gtk as gtk

from araclar import get_stock, mesaj_button

def check_image(file_name):
    """
    check if file is a valid image
    """
    if file_name.endswith(".svg"):
        return True
    try:
        with Image.open(file_name) as img:
            img.verify()
            if "gif" in img.format.lower():
                return False
            return True
    except (IOError, SyntaxError):
        return False

class Directory(GObject.Object):
    """
    define gobject propery to index list
    """
    __gtype_name__ = 'Directory'

    def __init__(self, file_id):
        super().__init__()

        self.file_id = file_id

WAIT = gdk.Cursor.new_from_name("wait")
DEFAULT_CUR = gdk.Cursor.new_from_name("default")

class OpenDirectory:
    """
    Open directory on call
    """
    error = None
    expanders = {}
    previous = []
    expand_widgets = {}
    child = {}
    directory = None
    parent = {}

    def __init__(self, *args):

        dialog, task, self.parent["window"] = args

        self.parent["box"] = self.parent["window"].get_child().get_last_child()

        if task and task.had_error():
            return None

        if dialog:
            try:
                directory = dialog.select_folder_finish(task).get_uri()
            except gi.repository.GLib.GError:
                return None

            url_data = PARSER.urlparse(directory)
            self.directory = PARSER.unquote(url_data.path)

        self.child["factory"] = gtk.SignalListItemFactory()
        self.child["list_store"] = Gio.ListStore(item_type=Directory)

        selection= gtk.SingleSelection.new(self.child["list_store"])
        selection.connect("selection-changed", self.select_changed)

        header_factory = gtk.SignalListItemFactory()
        header_factory.connect("bind", self.make_info_row)

        self.child["listview"] = gtk.ListView(
            model=selection,
            factory=self.child["factory"]
        )

        self.child["factory"].connect("setup", self.build_up_item)
        self.child["factory"].connect("bind", self.set_up_item, self.directory )


        self.child["listview"].props.margin_bottom = 48
        self.child["listview"] .set_header_factory(header_factory)

        self.parent["window"].add_custom_styling(self.child["listview"] )

        if isinstance(self.parent["box"].get_start_child(), gtk.ScrolledWindow):
            self.parent["box"].get_start_child().unrealize()

        self.parent["box"].set_start_child(gtk.ScrolledWindow(child=self.child["listview"]))
        self.parent["box"].set_resize_start_child(False)

        sw = self.child["listview"].get_parent()
        sw.props.margin_start = 12
        sw.props.margin_top = 2
        sw.set_policy(True, True)

        sw.set_has_frame(False)
        sw.set_size_request(220, 200)
        sw.add_css_class("wiki-scroll")

        self.parent["window"].add_custom_styling(sw)
        self.parent["window"].add_custom_styling(self.parent["box"])

        if dialog and task:
            self.create_list_view(self.directory)

        return None

    def create_list_view(self, directory):
        """
        create listview and rows
        """
        self.previous, files, dirs = [], [], []
        self.expanders, self.expand_widgets = {}, {}
        self.directory = directory
        self.parent["window"].gl_b["directory"] = directory

        self.child["list_store"].remove_all()

        self.setup = self.child["factory"].connect("setup", self.build_up_item)
        self.bind = self.child["factory"].connect("bind", self.set_up_item, directory )

        for each in os.listdir(directory):
            if os.path.isfile(directory +"/"+each):
                files.append(each)
            if os.path.isdir(directory +"/"+each):
                dirs.append(each)

        thread = Thread(target=self.append_target,
            args=(files, dirs)
        )
        thread.daemon = True
        thread.start()

        return True

    def append_to_parent_dir(self, each, item=None, name=None):
        """
        append to its parent directory
        get dirname
        get dir name without directory name
        remove leading "/" from taken name
        """
        dir_ = os.path.dirname(self.directory+"/"+each)
        dir_ = dir_.split(self.directory)[1]
        dir_ =  re.sub(r'^([^/]*)/', "", dir_ )

        if name:
            return dir_

        if dir_ in list(self.expanders):
            self.expanders[dir_][item.file_id] = item
        else:
            self.expanders[dir_] = {}
            self.expanders[dir_][item.file_id] = item

        return True

    def check_each(self, each_file):
        """
        append each file to dict
        each directory is key
        add each file to each key 
        """
        if os.path.isfile(self.directory+"/"+each_file):
            #list_store.append( Directory(each ) )
            item = Directory(each_file)
            self.append_to_parent_dir(each_file, item)

        if os.path.isdir(self.directory+"/"+each_file):

            self.expanders[each_file] = {}
            item = Directory(each_file)
            #   list_store.append( item )

            self.append_to_parent_dir(each_file, item)

            for n in os.listdir(self.directory+"/"+each_file):
                self.check_each(each_file+"/"+n )

    def append_target(self, files=list, dirs=list):
        """
        append files and directories
        """

        GLib.idle_add(self.child["listview"].set_sensitive, False)
        GLib.idle_add(self.parent["window"].set_cursor, WAIT)

        i = 0
        for i, each in enumerate(sorted(dirs)):
            self.check_each(each)
            name = self.append_to_parent_dir(each, name=True)
            GLib.idle_add(self.child["list_store"].append, self.expanders[name][each] )
            time.sleep(0.01)
            GLib.idle_add(self.child["listview"].scroll_to, i, 0)

        for x, each in enumerate(sorted(files)):
            GLib.idle_add(self.child["list_store"].append, Directory(each ) )
            time.sleep(0.020)
            GLib.idle_add(self.child["listview"].scroll_to, i+x, 0)

        GLib.idle_add(self.parent["window"].set_cursor, DEFAULT_CUR)
        GLib.idle_add(self.child["listview"].set_sensitive, True)

    def build_up_item(self, _, item):
        """
        factory build for each row
        """

        box = gtk.Box()
        label = gtk.Label(xalign=0, margin_start=8,
            margin_top=6, margin_bottom=6)

        box.append(get_stock("text-x-preview"))
        box.append(label)

        item.set_child(box)

    def make_expander_row(self, *args):
        """
        make expander row
        ...
        """
        file_id, file_path, item = args

        box = gtk.Box()
        box.props.margin_start = 8
        box.props.spacing = 4

        label = gtk.Label(label=file_id.split("/")[-1], margin_start=3, xalign=0)
        image = get_stock("folder-symbolic",size=12)

        label.set_tooltip_markup(
            "\n\t<tt><b>" +
            re.sub(r'^([^/]*)/', "", file_id ) +
            "</b></tt>\t\t\n\n"
            "<i>" + 
            "\t\t\n".join(sorted(self.expanders[file_id])).\
            replace(file_id+"/", "\t\t") +"</i>\n"
        )

        box.append(image)
        box.append(label)

        expander = gtk.Expander(label_widget=box)
        expander.set_tooltip_text(file_path)
        expander.props.margin_top = 12
        expander.props.margin_bottom = 12
        expander.props.margin_start =  12 * len(file_id.split("/"))
        expander.connect("activate", self.connect_expander)

        #if it's an empty dir
        if len(self.expanders[file_id]) < 1:
            expander.set_sensitive(False)

        # if it's already shown
        if file_id in list(self.expand_widgets):
            expander.set_expanded(self.expand_widgets[file_id]["expander"].get_expanded())
            #if not expanded set the image back to folder
            if not self.expand_widgets[file_id]["expander"].get_expanded():
                image.set_from_icon_name("folder-symbolic")

        # it builds up each time again
        self.expand_widgets[file_id] = {"expander":expander, "dir":item}

        item.set_child(expander)
        item.set_selectable(False)

    def set_expander_row(self,*args, **kwargs):
        """
        set styling expander on expand
        """
        default = {
            "dir_name":str, "size":12,
            "icon":"folder-symbolic",
            "markup":False, "fontsize":12
        }

        for i, each in enumerate(args):
            default[list(default)[i]] = each

        default = {**default, **kwargs}
        dir_name, size, icon, markup, fontsize = default.values()

        box = self.expand_widgets[dir_name]["expander"].get_label_widget()
        image = box.get_first_child()
        label = box.get_last_child()

        if markup:
            label.set_markup(f"<span size='{1024 * fontsize}'>"
                f"<b>{dir_name.split("/")[-1]}</b></span>")
        else:
            label.set_text(dir_name.split("/")[-1])

        image.set_pixel_size(size)
        image.set_from_icon_name(icon)

    def make_info_row(self, _, item):
        """
        make info row in header
        """

        box = gtk.Box(
            halign=gtk.Align.START,
            margin_start = 8,
            spacing = 16,
        )

        image = get_stock("folder-open-symbolic", size=24)
        image.set_tooltip_text("Click to have seperators")

        label = gtk.Label(use_markup=True, xalign=0.2,
            label=f"\n\n <big><b>"
            f"{os.path.basename(self.directory)}"
            "</b></big>\n\n"
        )

        box.append(image)
        box.append(label)

        box_end = gtk.Box(
            orientation=gtk.Orientation.VERTICAL,
            valign=gtk.Align.START,
            spacing = 6
        )
        box_end.append(box)
        box_end.append(gtk.Label(use_markup=True, xalign=0,
            label="<i><span  size='11776' weight='420'>"
            " ~../"
            f"{os.path.basename(
                os.path.dirname(self.directory)
            )} </span></i>\n\n"
            ),
        )
        box_end.set_tooltip_text(self.directory)

        event = gtk.GestureClick.new()
        box_end.add_controller(event)
        value = {1:False}
        event.connect("pressed", lambda *_:[
            value.update({1: not value[1]}),
            GLib.idle_add(self.child["listview"].set_show_separators,value[1])
        ])

        item.set_child(box_end)

    def set_up_label(self, *args ):
        """
        setup each label in the row
        """
        label, image, file_id, file_path = args
        label.set_tooltip_text(file_path)

        # give margin to each row relative to its sub position
        if "/" in file_id and file_id != self.directory:
            text =  os.path.basename(file_path)
            label.set_markup(f"<span  size='10240'>{text}</span>")

            label.props.margin_start = 8
            image.props.margin_start = 12 * len(file_id.split("/"))
            return False

        label.set_markup(f"<span  size='10240'>{file_id}</span>")
        return True

    def set_up_image(self, image, file_path):
        """
        setup image from stock
        """

        lang_name = self.parent["window"].guess_language(file_path, name=True)

        if check_image(file_path):
            stock = get_stock(pixbuf=file_path, size=32)
            image.set_from_paintable(stock.get_paintable())

        else:
            stock = self.parent["window"].operations.check_text_x(lang_name, lang_name, True)
            image.set_from_icon_name(stock.get_icon_name())

        stock.unrealize()

    def set_up_item(self, _, item, directory):
        """
        factory bind for each row
        """

        file_id = item.get_item().file_id
        file_path = directory+"/"+file_id

        box = item.get_child()

        if os.path.isdir(file_path):
            self.make_expander_row(file_id, file_path, item)
            return False

        if isinstance(box, gtk.Expander):
            if file_id not in self.expand_widgets or os.path.isfile(file_path):
        #        print("setup as box",file_id )
                box = gtk.Box(margin_start=1)
                label = gtk.Label(
                    margin_start=8,
                    margin_top=6, margin_bottom=6
                )
                box.append(get_stock("text-x-preview"))
                box.append(label)
                item.set_child(box)
                item.set_selectable(True)

        label = box.get_last_child()
        image = box.get_first_child()

        try:
            self.set_up_image(image, file_path)
            self.set_up_label(label, image, file_id, file_path)
        except AttributeError:
            pass

        if os.path.dirname(file_path) == self.directory:
            image.set_margin_start(8)
            box.set_margin_start(8)

        return True

    def clean_image(self, stock):
        """
        insert paintable into textbuffer
        time.sleep reason wht crazy iter error
        in an overloop
        somehow buffer.get_insert lagging behind
        ...
        """

        buffer = self.parent["window"].current_buffer
        parent  = self.parent["window"].current_editor.get_parent()
        try:
            buffer.disconnect_by_func(parent.update_tab_on_change)
        except TypeError:
            pass

        time.sleep(0.2)

        self.parent["window"].current_editor.set_sensitive(False)
        parent.set_sensitive(False)

        buffer.delete( buffer.get_start_iter(), buffer.get_iter_at_mark(buffer.get_insert()) )
        time.sleep(0.05)

        start = buffer.get_iter_at_mark(buffer.get_insert())

        self.parent["window"].current_editor.set_justification(2)
        self.parent["window"].current_editor.set_show_line_numbers(False)
        self.parent["window"].current_editor.set_highlight_current_line(False)

        time.sleep(0.1) #!
        buffer.insert_paintable( start, stock )
        time.sleep(0.03)
        buffer.set_modified(False)

        self.parent["window"].current_editor.set_pixels_above_lines(72)
        time.sleep(0.02)

    def select_changed(self, w, pos1, pos2 ):
        """
        if selection is an image
        show in new doc if new doc modified
        append new new doc..
        if it's a file check if it's open
        if it's open switch to that page
        else open new one
        ...
        """
        list_store = w.get_model()

        selection_index = w.get_selection_in_range(pos1, pos2)
        selection_index = selection_index.get_nth(0)

        item_from_selection = list_store.get_item(selection_index)

        file_ = self.directory +"/"+  item_from_selection.file_id
        files = self.parent["window"].operations.get_file_list()

        if not check_image(file_):
            for i, name in files.items():
                if name == file_:
                    self.parent["window"].notebook.set_current_page(i)
                    return False

            self.parent["window"].operations.yeni(file_)
            self.parent["window"].operations.open(file_)
            self.parent["window"].show_progress()
            return True

        stock = get_stock(pixbuf=file_, size=-1)
        stock = stock.get_paintable()
        width, height = stock.get_intrinsic_width(), stock.get_intrinsic_height()

        resize = (width + height) / 2

        if resize > 1000:
            while resize > 1000:
                resize = resize/2
            stock = get_stock(pixbuf=file_, size=resize)
            stock = stock.get_paintable()
        else:
            stock = get_stock(pixbuf=file_, size=384)
            stock = stock.get_paintable()

        for i, name in files.items():
            if name == file_:
                self.parent["window"].notebook.set_current_page(i)
                return True

        for i, name in files.items():
            if "New Document" in name:
                self.parent["window"].notebook.set_current_page(i)
                if not self.parent["window"].current_buffer.get_modified():
                    GLib.idle_add(self.clean_image,stock)
                    return False

        self.parent["window"].operations.yeni(False)
        GLib.idle_add(self.clean_image,stock)
        return False

    def insert_target(self, w, dir_name):
        """
        insert again into liststore
        """
        if dir_name not in list(self.expanders):
            return False

        total = len(self.expanders[dir_name])

        if total > 80:
            self.choose_one(w, dir_name, total)
            return False

        dirs, files = [], []

        def sort_function(file_):
            """
            put directories before choose_one
            """
            if os.path.isfile(self.directory +"/"+ file_):
                files.append(file_)
                return file_

            dirs.append(file_)
            return file_[0]

        for dir_index in range(self.child["list_store"].get_n_items()):
            each_item = self.child["list_store"].get_item(dir_index)
            if dir_name == each_item.file_id:
                break

        sorted( self.expanders[dir_name], key=sort_function, reverse=True)

        thread = Thread(target=self.insert_after,
            args=(dir_index, dir_name, dirs, files)
        )
        thread.daemon = True
        thread.start()
        return False

    def insert_after(self, *args):
        """
        insert files and dirs
        """
        dir_index, dir_name, dirs, files = args
        dir_index += 1

        GLib.idle_add(self.parent["window"].set_cursor, WAIT)

        GLib.idle_add( self.child["list_store"].splice,
            dir_index, 0, [ self.expanders[dir_name][each]
            for each in sorted(files) ]
        )

        GLib.idle_add( self.child["list_store"].splice,
            dir_index, 0, [ self.expanders[dir_name][each]
            for each in sorted(dirs) ]
        )

        if dir_index >= 0:
            GLib.idle_add( self.child["listview"].scroll_to,
                dir_index + 1, gtk.ListScrollFlags.FOCUS
            )

        GLib.idle_add(self.parent["window"].set_cursor, DEFAULT_CUR)

    def delete_target(self, w, dir_name):
        """
        delete given dir from list store
        ..
        """

        self.parent["window"].set_cursor(WAIT)

        for name in self.expanders[dir_name]:

            if os.path.isdir(self.directory +"/"+name):
                if self.expand_widgets[name]["expander"].get_expanded():
                    self.expand_widgets[name]["expander"].emit("activate")

        each = self.expand_widgets[dir_name]["dir"]
        each = each.get_item()
        result, position = self.child["list_store"].find(each)

        if not result:
            return False

        position +=1
        n_item = len(self.expanders[dir_name].values())

        self.child["list_store"].splice(
            position,
            n_item ,
            []
        )

        self.parent["window"].set_cursor(DEFAULT_CUR)
        GLib.idle_add(w.set_expanded, False)
        GLib.idle_add(self.child["listview"].scroll_to, position -1, 0)
        return True

    def choose_one(self, *args):
        """
        opens message dialog
        """
        w, dir_name, total = args

        soru = mesaj_button(
        heading=f"<b>Too many files to unpack\n{total} files within this directory..\n </b>",
        body="<span font-weight='400'><i>"
        "Click yes to open as a directory. "
        "Otherwise choosen directory will not be shown?</i></span>",
        buttons=["YES:2","NO:1"] )

        soru.set_size_request(400,-1)

        def response(widget, response_id):
            """
            choose reponse on end
            """
            response_id = int( widget.choose_finish(response_id) )
            match response_id:
                case 1:
                    GLib.idle_add(w.set_sensitive, False)
                    self.expanders[dir_name] = {}
                    GLib.idle_add(w.set_expanded, False)
                case 0:
                    self.create_list_view(self.directory +"/" + dir_name)

        soru.choose(self.parent["window"], None, response)

    def connect_expander(self, w):
        """
        list index key change during
        iteration for this reason
        recursive method with key > list used
        ...
        del or append rows on expand
        """

        dir_name= [k for k, v in self.expand_widgets.items() if v["expander"] == w ]
        dir_name = str(*dir_name)

        if not dir_name:
            return False

        if w.get_expanded():
            self.delete_target(w, dir_name)
            GLib.idle_add(self.set_expander_row, dir_name)

            if len(self.previous) >= 2 and dir_name in self.previous[-2]:
                self.set_expander_row(self.previous[-2],
                    16, "folder-open-symbolic", True, 12
                )
                self.previous.remove(self.previous[-2])

            return True

        self.insert_target(w, dir_name)

        if len(self.previous) > 0 and self.previous[-1] != dir_name:
            GLib.idle_add( self.set_expander_row, self.previous[-1],
                15, "folder-open-symbolic", True, 11
            )

        self.previous.append(dir_name)

        GLib.idle_add( self.set_expander_row, dir_name,
            18, "folder-open-symbolic", True, 13
        )

        return False
