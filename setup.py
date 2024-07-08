# -*- coding: utf-8 -*-

import setuptools import setup
import glob

setup (
    name = "Wiki Editor",
    version = "3.0",
    url = "https://github.com/anilcorekci/wiki-editor-3.0",
    author = "Anil COREKCIOGLU",
    author_email = "anilcorekci@gmail.com",
    description = "Gnome-text editor.",
    long_description = "PyGtk4 application designed to create, change, and enrich wiki contents.",
    platforms = "linux",
    requires = ["gir1.2-gtksource-5", "python3-gst-1.0", "gir1.2-vte-3.91", "libwebkitgtk-6.0-4"]
    data_files = [
        ('/usr/share/applications', glob.glob('./wiki-editor.desktop')),
        ('/usr/share/icons', glob.glob('./wiki-editor3.0/pyler/wiki-editor.png')),
        ('/usr/share/wiki-editor/pyler', glob.glob('./wiki-editor3.0/pyler/*.*')),
        ('/usr/share/wiki-editor/templates', glob.glob('./wiki-editor3.0/templates/*.*')),
        ('/usr/share/wiki-editor/ICONS', glob.glob('./wiki-editor3.0/ICONS/*.*')),
        ('/etc/apparmor.d', glob.glob('./wiki-editor3.0/etc_apparmor.d/Wiki-Editor')),
        ],
    scripts = ['Wiki-Editor'],
)
