# -*- coding: utf-8 -*-
"""
set current buffer text
"""

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import Pango as pango

DEFAULT_COLOR = "rgba(127, 82, 122, 0.950)"

class SetText():
    """
    define colors and pango font
    """
    flag = gtk.TextSearchFlags.TEXT_ONLY
    fg = gdk.RGBA()

    underline = gdk.RGBA()
    underline.parse("rgba(233, 42, 99, 0.400)")

    n_text = gdk.RGBA()
    n_text.parse("#3F8B79")

    def __init__(self, current_buffer,  text, insert=None, color=DEFAULT_COLOR):
        """
        pass arguments to class
        set current self.buffer self.text
        """
        self.buffer = current_buffer
        self.text = text
        self.insert = insert
        self.color = color

        fg = gdk.RGBA()
        fg.parse(self.color)

        self.tag = self.buffer.create_tag(
            underline_rgba=self.underline,
            left_margin=1,
            right_margin=1,
            stretch=7,
            stretch_set=True,
            foreground_rgba=fg,
            underline=4,
        )

        self.apply()

    def set_instances(self):
        """
        set instance of tags
        in pango markup
        """
        start_tag, end_tag = self.text[0], self.text[2]
        
        match end_tag:
            case "'''":
                self.tag.set_property("weight", pango.Weight.BOLD)

            case "''":
                self.tag.set_property("style", pango.Style.ITALIC)
            
            case "</big>":
                self.tag.set_property("scale", 1.4)
                self.tag.set_property("underline-set", False)

            case "</small>":
                self.tag.set_property("scale", .7)

            case "</sup>":
                self.tag.set_property("rise", 1024*7)
                self.tag.set_property("scale", .9)

            case "</sub>":
                self.tag.set_property("rise", -1024*7)
                self.tag.set_property("scale", .9)

        match start_tag:
            case start_tag if "blue" in start_tag:
                self.fg.parse("blue")
                self.tag.set_property("foreground_rgba", self.fg)

            case start_tag if "red" in start_tag:
                self.fg.parse("red")
                self.tag.set_property("foreground_rgba", self.fg)

            case start_tag if "code" in start_tag:
                self.fg.parse("rgba(192, 191, 188, 0.723)")
                self.tag.set_property("background-rgba", self.fg)
            #    self.tag.set_property("paragraph_background","#808080")
                self.fg.parse("rgba(1, 28, 23, .8)")
                self.tag.set_property("foreground-rgba", self.fg)
                self.tag.set_property("underline-set", False)
            #    self.tag.set_property("indent", 20)

            case "[":
                self.tag.set_property("underline", 1)

            case "[[":
                self.tag.set_property("underline", 2)

            case "==":
                self.tag.set_property("underline-set", False)
                self.fg.parse(self.color)
                self.tag.set_property("scale", 1.1)

                if "==" in self.text[1]:
                    self.tag.set_property("scale", 
                        1.1 + len(self.text[1].split("==")) / 10
                    )

    def apply(self):
        """
        apply text changes
        ..
        """
        if self.insert:
            self.insert_text()
            return True

        start, end = self.buffer.get_selection_bounds()
        self.buffer.begin_user_action()

        self.buffer.delete(start, end)
        iter_ = self.buffer.get_iter_at_mark(self.buffer.get_insert())

        if isinstance(self.text, list):        
            self.set_instances()
            self.buffer.insert_at_cursor("".join(self.text))

            self.find_each(0)
            self.find_each(2)

            start, end = self.find_each(1, each_tag=self.tag)
            self.buffer.select_range(start, end)
            self.buffer.end_user_action()
            return False

        self.buffer.insert_at_cursor(self.text)
        iter_ = self.buffer.get_iter_at_mark(self.buffer.get_insert())

        start, end = iter_.backward_search( self.text,
            gtk.TextSearchFlags.TEXT_ONLY, 
            None 
        )

        self.tag.set_property("underline", False)
     #   self.tag.set_property("background_rgba", self.n_text)

        self.buffer.apply_tag(self.tag, start, end)
        self.buffer.select_range(start, end)
        self.buffer.end_user_action()

        return False

    def insert_text(self):
        """
        insert text after cursor
        """
        self.buffer.begin_user_action()
        self.buffer.insert_at_cursor(self.text)

        if self.color != DEFAULT_COLOR:
            iter_ = self.buffer.get_iter_at_mark(self.buffer.get_insert())
            start, end = iter_.backward_search(self.text, self.flag, None)
            self.tag.set_property("underline", False)

            self.buffer.apply_tag(self.tag, start, end)

        self.buffer.end_user_action()

    def all_search(self, in_tag, start):
        """ 
        search for match for appyling 
        custom tag
        """
        all_search = self.text[1].split(self.text[in_tag])
        count_match = all_search.count("")

        if self.text[0] == self.text[2]:
            count_match += len(self.text[1])

        if len(all_search[0]) > 1:
            count_match += len(self.text[1].split(self.text[in_tag])) -1

        i = 0
        while i < count_match:
            i+=1
            found = start.backward_search( self.text[in_tag], self.flag, None )
            if not found:
                continue
            try:
                start, end = found
            except UnboundLocalError:
             #   print("fixed..")
                break

        try:
            return start, end
        except UnboundLocalError:
            end = start.copy()
            end.forward_word_end()
            #print("fixed..")
            return start, end

    def find_each(self, in_tag, each_tag=None):
        """
        re-color inset and outset of text tag
        """

        iter_ = self.buffer.get_iter_at_mark(self.buffer.get_insert())

        start, end = iter_.backward_search(self.text[in_tag], self.flag, None)

        # fix for mathching brackets and over apply...
        if self.text[in_tag] in self.text[1] and in_tag == 0:
            start, end = self.all_search(in_tag, start)

        # if tag one equal to tag 2
        elif in_tag == 0 and self.text[0] == self.text[2]:
            #you must find the first instance of the
            #tag
            all_search = len(self.text[1].split(self.text[0]))
            i=0 #check this one again with count.("") ...
            while i < all_search:
                #find how many instance included and
                #search back to the start...
                start, end = start.backward_search( self.text[in_tag], self.flag, None)
                i+=1

        if not each_tag:
            each_tag = self.buffer.create_tag(foreground_rgba=self.n_text)

        self.buffer.apply_tag(each_tag, start, end)
        return start, end
