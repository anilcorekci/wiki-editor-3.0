#*-* coding: utf-8 -*-
"""
Takes argument from notebook.py
notebook is a toplevel 
gtk.ApplicationWindow class
"""

import os
import re
from  urllib import parse as PARSER

from gi.repository import Gtk as gtk
from gi.repository import Gio
from gi.repository import GLib

from wikitext import WikiText
from tercihler import ConfigWindow

from araclar import (hata, mesaj,
    get_filechooser, get_stock, mesaj_button )

UNDEFINED = "New Document"


class FileOperation():
    """
    File Operations for wiki editor gui
    """
    udf_list = {} # undefinded_list

    def __init__(self, wiki_editor):

        self.wikieditor = wiki_editor
        self.gl_b = wiki_editor.gl_b
        self.notebook = wiki_editor.notebook
        self.ileti = wiki_editor.ileti
        self.add_custom_styling = wiki_editor.add_custom_styling
        self.set_text = wiki_editor.set_text

    def note_label_box(self, label_text, yol):
        """
        create Centerbox for page title and return
        """
        if self.notebook.get_n_pages() >= 1:
            self.notebook.set_show_tabs(True)

        box1 = gtk.CenterBox()
        box1.set_hexpand(True)
        
        label = gtk.Label(label=label_text, xalign=0.5)
        label.set_ellipsize(3)
        label.set_halign(gtk.Align.CENTER)
        label.set_width_chars(17)

        box = gtk.Box()
        box.append(label)

        box1.set_center_widget(box)
        label.set_tooltip_text(f"File Path: {yol}")

        image1 = get_stock("application-exit-symbolic")
        image1.set_halign(gtk.Align.END)

        event = gtk.GestureClick.new()
        image1.add_controller(event)
        image1.set_tooltip_text("Close Document" )

        image1.set_size_request(12, 12)
        event.connect("pressed", lambda *_: self.kapat(_, label_text) )
        box1.set_end_widget(image1)

        return box1

    def get_file_path(self, label=None ,tab=None):
        """
        find label in tab returns it or
        its tooltip
        """
        if tab:
            center_box = tab[0].get_tab_label(tab[1])
        else:
            center_box = self.notebook.get_tab_label(
                self.wikieditor.current_editor.get_parent()
            )

        hbox = center_box.get_center_widget()
        label_widget = hbox.get_last_child()

        if label:
            return label_widget

        return label_widget.get_tooltip_text()

    def yeni(self,yol, baslik=str):
        """
        create new tab with wikitext
        """
        page_number = self.notebook.get_current_page() + 2

        if not os.path.isfile(yol):
            baslik = f"{UNDEFINED} : {page_number}"
            yol = baslik
            # IF UNDEFINED NAME EXIST IN NOTEBOOK...
            if yol in [ self.udf_list[n] for n in self.udf_list]:
                #DEFINE NEW UNDEFINED AS +1 FROM THE CURRENT MAX NUMBER IN THE LIST
                page_number = max(list( int(
                    self.udf_list[n].split(":")[1])\
                    for n in self.udf_list
                ) )

                baslik = f"{UNDEFINED} : {page_number + 1}"

            self.udf_list[int(page_number)] = baslik

        else:
            baslik = yol
            for i in re.findall(".*?../", baslik):
                baslik=baslik.replace(i, "")

        page_title = self.note_label_box( baslik, yol)
        wiki_text = WikiText(self.ileti, self.wikieditor.hamburgers)

        self.notebook.append_page( wiki_text, page_title)
        self.notebook.set_tab_reorderable(wiki_text,True) #!!
    #    self.notebook.set_tab_detachable(wiki_text, True)
    # https://docs.gtk.org/gtk4/method.Notebook.set_tab_detachable.html

        i = -1
        while i < self.notebook.get_n_pages():
            i+=1
            self.notebook.next_page()

        if self.gl_b["overlay"] and self.gl_b["overlay"].get_margin_top() != 46:
            self.gl_b["overlay"].set_margin_top(46)

        #self.gl_b.update( {"grid": False} )
        self.add_custom_styling(wiki_text)
        self.add_custom_styling(self.notebook)

        self.wikieditor.current_buffer.emit("cursor-moved")

        ConfigWindow(self.wikieditor).set_ayar(set_up=True)

    def kapat(self, _, label_text):
        """
        close operation for both tab and toplevel window
        """
        def close():
            if self.notebook.get_n_pages() == 1:
                GLib.idle_add( self.notebook.set_show_tabs, False)
                if self.gl_b["overlay"]:
                    self.gl_b["overlay"].set_margin_top(0)

        i=-1
        while i < self.notebook.get_n_pages():
            i+=1
            self.notebook.set_current_page(i)

            get_n_widget = self.notebook.get_nth_page(i)
            # return wiki_editor
            get_n_widget = self.get_file_path(label=True)
            # return label
            get_n_info = get_n_widget.get_text()
            # get_text

            if label_text != get_n_info:
                continue

            # if get_n_info in self.udf_list
            if get_n_info in [ self.udf_list[n] for n in self.udf_list]:

                #REMOVE get_n_info from self.udf_list, REDUCE -1 each given index
                self.udf_list = {key-1: val for key, val in self.udf_list.items() if key != i+1 }

                # REDEFINE index info from 1 to N large from UNDEFINED INFO
                self.udf_list = {key: self.udf_list[val] for key, val in \
                                  zip(range(1,len(self.udf_list)+1), self.udf_list ) }

            if self.wikieditor.current_buffer.get_modified():

                dialog = mesaj_button(
                body= "<span font-weight='500'><i>Document contains unsaved changes," +
                    " changes which are not saved will be lost permanently.</i></span>",
                heading=" <span font-size='"+f"{1024*14}'"+
                    " gravity='west'"+"><b>'"+ label_text + \
                    "'</b> <small>save changes?"
                    "</small></span> ",
                buttons=[ "Discard:2","Cancel:0", "Save:1"] )

                self.wikieditor.set_sensitive(False)

                def resp(widget, response_):
                    self.wikieditor.set_sensitive(True)
                    response_ = int( widget.choose_finish(response_) )

                    match response_:
                        case 2:
                            self.kayit()
                        case 1:
                            pass
                        case 0:
                            self.notebook.remove_page(i)
                            close()

                dialog.choose(self.wikieditor, None, resp)
          #      self.add_custom_styling(dialog)

            else:
                self.notebook.remove_page(i)

            break

        close()

    def get_file_list(self):
        """
        return filenames in a dict
        """
        files = {}
        i = -1

        while i < self.notebook.get_n_pages():
            i+=1
            if self.notebook.get_n_pages() <= 0:
                break

            self.notebook.set_current_page(i)
            label = self.get_file_path()
            file_path = "".join(label.split(":")[1:3])
            files[i] =  re.sub(r"^\s+", "", file_path)

        return files

    def open_file(self, _):
        """
        open new file from path
        """
        def response_(_, res_id):
            """
            apply chosen on response..
            """
            files = self.get_file_list()

            if not res_id.had_error():
                file_uri = dialog.open_finish(res_id).get_uri()
                url_data = PARSER.urlparse(file_uri)
                file_name = PARSER.unquote(url_data.path)

                for i, name in files.items():
                    if name == file_name:
                        self.notebook.set_current_page(i)
                        self.ileti.set_markup("<b>"+
                            f"<i>The file : {os.path.basename(file_name)}</i>"+\
                            "</b> is already open..")
                        return False

                self.yeni(file_name)
                self.open(file_name)
                self.wikieditor.show_progress()

            return True

        dialog = get_filechooser(self.wikieditor,
                    desc_="Choose a file to read and modify..")
        dialog.open(self.wikieditor, None, response_)

    def open(self, dosya):
        """ open given filepath """
        try:

            with open(dosya, "r", encoding="utf-8" ) as das:
                try:
                    self.set_text( das.read(), True )
                except UnicodeDecodeError as err:
                    hata(f"Error code:5 \n\tError message:{dosya}\
                         \n\tAn error occured while reading the file!\n{err}\n\n", self.wikieditor)
                    return False

        except IOError as msj:
            hata(f"{dosya}\n\tFile cannot be opened\n\
                 \tError code:-3\n\tError message:{msj}\n\n\n", self.wikieditor)
            return False

        language = self.wikieditor.guess_language(dosya)

        self.wikieditor.current_buffer.set_language(language)
        self.wikieditor.current_buffer.set_enable_undo(False)
        self.wikieditor.current_buffer.set_enable_undo(True)
        self.wikieditor.current_buffer.set_modified(False)

        return True


    def kayit(self, *_, save_as=None):
        """
        save current buffer file
        """
        label = self.get_file_path()

        file_path = "".join(label.split(":")[1:3])
        file_path =  re.sub(r"^\s+", "", file_path)
#        print(file_path)
        
        if not os.path.isfile(file_path) or save_as:

            dialog = get_filechooser(self,
                desc_="Save recent changes..",
                type_="SAVE"
            )

            dialog.set_initial_name(os.path.basename(file_path))
            directory = os.path.dirname(file_path)

            if os.path.isdir(directory):
                directory = Gio.File.new_for_path(directory)
                dialog.set_initial_folder(directory)

            def on_change(_, response):
                if response.had_error():
                    return False

                file_uri = dialog.save_finish(response).get_uri()
                url_data = PARSER.urlparse(file_uri)
                bilgi = PARSER.unquote(url_data.path)

                konu = self.wikieditor.get_konu(True)

                try:
                    with open(bilgi ,"w", encoding="utf-8") as dosya:
                        dosya.write(konu)
                        page = self.notebook.get_current_page()
                        self.notebook.remove_page(page)
                except IOError as msj:
                    mesaj(f"{bilgi}\nFile cannot saved..\
                            \nError code:-1\nError message:{msj}", pencere=self.wikieditor)

                self.yeni(bilgi)
                self.open(bilgi)
                self.wikieditor.show_progress()
                return True

            dialog.save(self.wikieditor, None, on_change)
            return True

        konu = self.wikieditor.get_konu(True)

        try:
            with open(file_path, "w", encoding="utf-8") as dosya:
                dosya.write(konu)
                self.ileti.set_markup(
                        f"<small>\t{os.path.basename(file_path)}"
                        "\n\tfile saved.</small>"
                    )
                self.wikieditor.current_buffer.set_modified(False)
        except IOError as msj:
            mesaj(f"{file_path} File cannot be saved.." + \
                    f"Error Code:-2\nError message:{msj}",
                    pencere=self.wikieditor )
            return False

        self.wikieditor.show_progress()
        return True
