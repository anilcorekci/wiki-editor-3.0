#!/bin/python3.12
"""
terminal emulator for wikieditor
"""
import os

from araclar import TMP_FILE

from gi.repository import Gtk as gtk
from wikitext import WikiText

WIKI_LOG = "/tmp/wiki-editor.log"

class Terminal:

    line_number = 0
    iter_at_line = None
    ileti = gtk.Label()
    end = None
    def __init__(self):
        self.ileti = gtk.Label()
        self.sw = WikiText(self.ileti)

        self.sw.set_size_request(-1, 300)

        self.editor = self.sw.get_child()
        self.editor.set_property("overwrite", True)
        menu =self.editor.get_extra_menu()
        self.editor.connect("backspace", self.set_editable)
        menu.remove_all()

        self.editor.add_css_class( "terminal")

        self.buffer = self.editor.get_buffer()
        self.buffer.set_enable_undo(False)
        self.buffer.connect("end-user-action", self.catch_enter)
        self.trigger_on_enter("")

    @property
    def interface(self):
        return self.sw

    def set_editable(self, *_):
        start, end = self.buffer.get_bounds()
        string = start.get_text(end)
    #    print(string[-1:-4])
        if ":~$" == string[-4:-1]:
     #       print(string, "**")
            self.buffer.insert_at_cursor(" ")

    def catch_enter(self, buffer):

        iter_ = buffer.get_end_iter()
        found = iter_.backward_search(os.path.basename(os.environ["PWD"])+":~$",
            gtk.TextSearchFlags.TEXT_ONLY)
        start, end = found
        text = iter_.get_text(end)
        start, end = end.copy(), end.copy()

        end.forward_to_end()
        start.forward_to_end()

        start.backward_char()

        text_end = start.get_text(end)
  #      print(text, text_end)

        if self.line_number == 0 and "\n" in text:
            self.append_output(text)
            self.trigger_on_enter("")
            self.line_number +=1

        elif "\n" in text_end:
            self.append_output(text)
            self.trigger_on_enter("")
            self.line_number +=1

    def trigger_on_enter(self, code):

        self.buffer.begin_irreversible_action()
        
        self.buffer.insert_interactive(
            self.buffer.get_end_iter(),
            os.path.basename(os.environ["PWD"])+":~$ " + code,
            -1, True)
        self.buffer.end_irreversible_action()

        """tag = self.buffer.create_tag( foreground="white",
                paragraph_background="blue",
                right_margin=0,
                indent=50,
                left_margin=0,
                size_points=13.0,
                wrap_mode=gtk.WrapMode.WORD )
        """
        start, end = self.buffer.get_bounds()
  #      self.buffer.apply_tag(tag, start, end)
        self.buffer.delete_interactive(start, end, False)
        self.buffer.backspace(start, False, False)
        end.editable(False)
        self.buffer.set_modified(False)

        self.editor.reset_cursor_blink()


    def append_output(self, code):
        if len(code) < 3:
            return False

        self.buffer.begin_irreversible_action()

        match code:
            case code if "cd" in code:
                print(f"{code}".splitlines())
            case code if "./" in code:
                print(f"{code}".split("./"))
            case _:
                pass


        with open(TMP_FILE, "w", encoding="utf-8") as dosya:
            dosya.write(code.replace("\n"," ") + "> "+ WIKI_LOG)

        os.system(f"chmod +x {TMP_FILE}")

        os.system(TMP_FILE)

        with open(WIKI_LOG, "r", encoding="utf-8") as dosya:
            self.buffer.insert_at_cursor(dosya.read())

     #   os.system(f"rm -rf {TMP_FILE}" )

        self.buffer.end_irreversible_action()
        return True
