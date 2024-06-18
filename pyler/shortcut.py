# -*- coding: utf-8 -*-

from gi.repository import Gtk as gtk

class ShowShortCuts(gtk.ShortcutsWindow):
    """
    show shortcuts
    ...
    """
    group = None
    keys = ["<primary>","<shift>","F","<alt>"]
    action_filter = {"ToolBar": []}
    items = []

    def __init__(self, action_1, action_2, app=None):
        gtk.ShortcutsWindow.__init__(self)
        self.set_property("modal",True)

        try:
            #it doesn't work as in xml so...
            searchbar = self.get_first_child().get_first_child()
            searchbar.set_visible(False)
        except AttributeError:
            pass

        if len(self.action_filter["ToolBar"]) == 0:
            self.filter_simgeler(action_2)

        self.iterate_dict(self.action_filter)
        self.iterate_dict(action_1)

        self.set_transient_for(app)
        app.set_help_overlay(self)
        app.add_custom_styling(self)
        self.present()

    def filter_simgeler(self, action_2):
        """
        parsing shortcuts from SIMGELER
        """
        for i in action_2:
            try:
                name, shortcut = i[0], i[-1][-1][-1]
            except KeyError: # as err:
                """
                print("KeyError", err)
                print("this was expected if shotruct is given in a dict")
                print("then take the first agrument of dict as a shortcut")
                """
                shortcut = i[-1][-1]
                pass
     
            for found in self.keys:
                if found in shortcut:
                    self.action_filter\
                    ["ToolBar"].\
                    append( [name, shortcut ] )

            name, item = i[0], i[-1][-1]

            if not item or type(item) is not dict:
                continue

            item = list(item.keys())[0]

            if item is None:
                continue

            for found in self.keys:
                if found in item:
                    self.action_filter["ToolBar"].\
                        append([name, item])

    def iterate_dict(self, dict_):
        """
        define shortcut section and groups
        for each key append new group
        """
        for each, itemlist in dict_.items():

            each = each.replace("_"," ").title()

            section = gtk.ShortcutsSection()

            section.set_property("section-name", each)
            section.set_property("title", each)
            section.set_property("max-height", 10)

            self.group = gtk.ShortcutsGroup()
         #   self.group.set_property("title", each)
        #    self.group.set_property("view", each)

            section.add_group(self.group)
            self.add_section(section)
            self.add_list(itemlist)

    def add_list(self, itemlist):
        """
        add shortcut into shorcut group
        ...
        """
        for keys in itemlist:
            if callable(keys[-1]):
                continue

            short_cut_ = gtk.ShortcutsShortcut()
            short_cut_.set_property("title", keys[0])

            if type(keys[-1]) is bool :
                if keys[-2] is None:
                    continue
                short_cut_.set_property("accelerator", keys[-2])
            else:
                short_cut_.set_property("accelerator", keys[-1])

            short_cut_.set_property("shortcut-type", gtk.ShortcutType.ACCELERATOR )

            short_cut_.set_direction(gtk.TextDirection.RTL)
            self.group.add_shortcut(short_cut_)
