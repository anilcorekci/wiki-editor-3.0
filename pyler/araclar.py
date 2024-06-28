# -*- coding: utf-8 -*-
#pylint: disable=E0611
"""
Tools and string variable used in WikiEditor Toplevel
"""
import subprocess as sp_
import gi

from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf, Gio
from gi.repository import Adw

gi.require_version('Gtk', '4.0')
gi.require_version("GtkSource", "5")
TMP_FILE = "/tmp/wiki-editor"

###LIST OF LANGUAGES
# WILL BE SHOWN IN A HAMBURGER CALLED LANGUAGES
############################
LANGS = {"text/plain":"text/plain",
        "C":"text/x-csrc",
        "Css":"text/css",
        ".desktop":"application/x-desktop",
        "Html":"text/html",
        "Glade":"application/x-glade",
        "Python":"text/x-python",
        "Java":"text/x-java",
        "PHP":"application/x-php",
        "Perl":"application/x-perl",
        "Xml":"application/xml",
        "Sh":"application/x-shellscript"}
###icons############################pwd
#
def resim(yol):
    """
    Retrun gtk Image from given file_path
    """
    image  = gtk.Image()
    image.set_from_file(yol)
    return image

descriptions = {
#Description # in a list > text before > text after < shortcut key
# if you don't want to define shortcut keep the list size 2
"A set of tag for bold text":["'''" ,"'''", "<primary>B"],

"A set of tag for italic text":  ["''" ,"''", "<primary>K"] ,

"Apply heading to selected text \n Repeat the process to append  sub-heading.":
["==" ,"==", "<primary>T"],

"Superscript text insertion.":  ["<sup>" ,"</sup>", "<alt><shift>s"],

"Subscript text insertion.":  ["<sub>" ,"</sub>", "<alt>d"],

"Big text insertion.":  ["<big>" ,"</big>", "<alt>b"],

"Small text insertion.":  ["<small>" ,"</small>", "<alt>s"],

"A set of tag to link to an existing wiki-page.":  ["[[" ,"]]"],

"Color select with custom span": "color_select",

"Font select with custom span": "font_select",

"To write in red":["{{red|" ,"}}"],

"To write in blue" : ["{{blue|" ,"}}"] ,

"A set of tag to insert image or media": ["[[File:" ,"|thumb]]"],

"A set of tag to redirect link" : ["[" ,"]"] ,

"Need to have a nowiki tag?" : ["<nowiki>" ,"</nowiki>"],

"A set of tag for codes": ["{{code|<nowiki>" ," </nowiki>}} <br>"],

"Komutlar için uçbirim şablonu" :["{{uçbirim|\n<nowiki>" ,"</nowiki>}}"] ,

"Dosya içerikleri  için wiki şablonu":  ["{{dosya|nerde bu dosya|\n" ,"}}"],

"Yazının Hangi sürüm için olduğunu seçin": ["{{sürüm|" ," }}"] ,

"SUDO alıntıları için bir  şablon":{
# key for shortcut
# format for window
# if no shortcut wanted simply define it as None
#whatever given before = defined as label and
#for each format {} reperesents entry..
#to append '{' or '}' < these characthers
#add 2 for each one to be presented in text.

    None: "{{{{dergi|\
sayı={}|tarih={}|\
sayfano={}|yazar={}\
}}}}"
    },

"Mozilla Firefox Eklentileri için bir şablon.":{
    None: \
    "{{{{\
firefoxeklentisi|isim={}|ekran_görüntüsü={}|açıklama={}\
|geliştirici={}||web_sitesi={}\
}}}}"
    },

"A template creator for Infobox software.": {
    "<primary>0": \
    "{{{{Infobox software|\
name={}|screenshot={}|caption={}\
|developer={}|genre={}|license={}|\
operating system={}|website={}\
}}}}"
    },

"Yazınız için bir kategori seçin..": "kategori",
}

ICONS = {}
# looking for simgler folder
# for each filename it looks for descriptions
# if it finds exact match in descriptions with filename
# defines it as a title
# example title name:
# '02-bold.png'
# before - to define its placement in a toolbar
# can be number abc etc...

for simge in sp_.getoutput("ls ../ICONS").splitlines():
    simge_adi = simge.split(".")[0].split("-")[1]
    for aciklama in descriptions:
        if simge_adi.lower() in aciklama.lower():
            break

    ICONS[simge_adi.title()] = ([
        aciklama.title(),
        resim("../ICONS/" + simge),
        descriptions[aciklama]
    ])

#############################################################################
HAK = gtk.Image()
HAK.set_from_pixbuf(
    GdkPixbuf.Pixbuf.new_from_file_at_size(
        "wiki-editor.png", 28,28)
    )
###Hakkında####################################################
PROGRAM="Wiki Editor "
#
LOGO ="wiki-editor.png"
#
VERSION="3.0"
#
WHO="copyright© hitokiri"

#
MAIL = ["Anıl Çörekcioğlu  <anilcorekci@gmail.com>"]
#

##Kategoriler####################################
#
# categoreis dictionary
# each key present different stored list
# each list item will be shown in a ComboBox...
# under key with checkbox..
CATEG= {
"temel": ["Temel Bilgiler","Açık Kaynak Ünlüleri","Kurulum","Nasıl Belgeleri",
    "Sss","Temel Açık Kaynak Bilgileri","Temel Bilgisayar Bilgileri",
    "Temel İnternet Bilgileri","Önemli İnternet Siteleri",
    "Temel Linux Bilgileri","Ubuntu Kaynakları "],
#
"donanim" : ["Donanım", "Ağ kartları", "Grafik", "Grafik Kartları",
    "Monitörler", "Masaüstü Bilgisayarlar",
    "Netbook Bilgisayarlar", "Notebook Bilgisayarlar",
    "Ses Kartları", "Usb Aygıtlar", "Tv Kartları",
    "Yazıcı-Tarayıcı", "İşlemci-ram", "Diğer Donanımlar"],
#
"yazilim": [ "Yazılım", "Ağ","Diğer Yazılımlar", "Donatılar",
    "Dosya Sistemleri", "Grafik Yazılımları", "Güvenlik",
    "İnternet Yazılımları", "İşletim Sistemleri", "Diğer Linux Dağıtımları",
    "Linux Mint", "Masaüstü","Görsellik", "Masaüstü Yöneticileri",
    "Microsoft Windows Yazılımları", "Ofis Yazılımları", "Oyun",
    "Programlama", "Programlama Dilleri",
    "Sanallaştırma", "Ses ve Video Yazılımları",
    "Sistem Uygulamaları", "Sunucu Uygulamaları"],
#
"Ubuntu": ["Ubuntu", "Ubuntu Sürümleri", "Paylaşım",
           "Tayfa", "Tayfa Toplantıları",
           "Ubuntu Hakkında", "Ubuntu Türevleri",
           "SUDO Alıntıları", "Ekran Görüntüleri"],
}

################################################
# sed commands for parsing texts
# it can be done in many different way
# however sed simply makes it easier
# Selection content given in as a function arg
# it writes the outcome into TMP_FILE
# another function will read the file in
# MenuItems class
# and remove TMP_FILE after inserting text..
# see set_tool_edit
####################################################
NO = r'''sed -i -e 's_>_<nowiki>></nowiki>_g' {}
sed -i -e 's_#_<nowiki>#</nowiki>_g' {}
sed -i -e 's_=_<nowiki>=</nowiki>_g' {}
sed -i -e 's_*_<nowiki>*</nowiki>_g' {}
sed -i -e 's_}}_<nowiki>}}</nowiki>_g' {}
sed -i -e 's_{{_<nowiki>{{</nowiki>_g' {}
sed -i -e 's_|_<nowiki>|</nowiki>_g' {}
sed -i -e 's_\[_<nowiki>[</nowiki>_g' {}
sed -i -e 's_]_<nowiki>]</nowiki>_g' {}
sed -i -e 's_~_<nowiki>~</nowiki>_g' {}'''.format(*[TMP_FILE]*10)
####################################################
RNO = r'''sed -i -e 's_<nowiki>__g' {}
sed -i -e 's_</nowiki>__g' {}'''.format(*[TMP_FILE]*2)
####################################################
BOSLUK = r'''sed -i -e 's_ _\&nbsp;_g' {};
sed -i -e 's_    _\&nbsp;\&nbsp;\&nbsp;\&nbsp;_g' {};
sed -i -e 's_    __g' {};
a=`sed "s/$/<br>/" {} > /tmp/wiki`
cat /tmp/wiki > {}
rm -rf /tmp/wiki '''.format(*[TMP_FILE]*5)
####################################################
RBOSLUK = r"""sed -i -e 's_\&nbsp;_ _g' {};
sed -i -e 's_<br>__g' {}""".format(*[TMP_FILE]*2)
####################################################
MADDE = f"""sed -i 's/^/*/' {TMP_FILE}"""
####################################################
RMADDE = f"""sed -i -e 's_*__g' {TMP_FILE}"""
####################################################
NU = f"""sed -i 's/^/#/' {TMP_FILE}"""
####################################################
NOU = f"""sed -i -e 's_#__g' {TMP_FILE}"""
####################################################

# DEFINE MENU ITEMS INFO
# IN MENUSETUP DICTONARY
MENUSETUP = {
# SED COMMANDS
# this can have multiple key if needed
# key > dict > list(os command, shortcut)
    "ARACLAR":{
    "Numbered": [ NU, "<alt>M" ],
    "Del Numbered": [ NOU,"<alt><shift>M"],
    "All Nowiki": [ NO, "<alt>N" ],
    "Del Nowiki": [ RNO, "<alt><shift>N"],
    "Bullets": [ MADDE, "<primary>E" ],
    "Del Bullets": [ RMADDE, "<primary><shift>E"],
    "Breaks": [ BOSLUK, "<primary>W"],
    "Del Breaks":[ RBOSLUK, "<primary><shift>W" ],
    }
}

################UI INFO MENU AŞAMALARI######################################

def hakkinda(*_, app=None):
    """
    About Window
    """
    aboutdialog = Adw.AboutWindow(
        application_name=PROGRAM,
        application_icon="wiki-editor",
        issue_url="https://github.com/anilcorekci/wiki-editor-3.0",
        copyright="2010-2024 " + WHO,
        developer_name=WHO,
        transient_for=app,
        version=VERSION,
        license_type=gtk.License.GPL_3_0
    )
    aboutdialog.set_resizable(False)
    aboutdialog.set_size_request(-1, 525)
    aboutdialog.add_credit_section("MAIL", MAIL)
    app.add_custom_styling(aboutdialog)
    aboutdialog.present()

def get_stock(stock_=None, pixbuf=None, size=48):
    """
    returns stock image from given stock_name or pixbuf file
    """
    image_ = gtk.Image()
  #  print(dir(image_))
  #  image_.new_from_icon_name(stock_ )

    if pixbuf:
        image_.set_pixel_size(size)
        image_.set_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_size(
                pixbuf, size, size)
        )
  #      image_.set_margin_start(12)
        return image_

    return image_.new_from_icon_name(stock_ )

def get_filechooser(pencere=None, desc_=None, type_="OPEN"):
    """
    Returns response and dialog
    shows filechooser
    """
    dialog = gtk.FileDialog( title=desc_,
            modal=pencere, accept_label= type_)

   # dialog.set_default_response(gtk.ResponseType.OK)
#    dialog.set_icon_from_file("wiki-editor.png")
    filter_ = gtk.FileFilter()
    filter_.set_name("Tüm Dosyalar")
    filter_.add_pattern("*")

    txt = gtk.FileFilter()
    txt.set_name("txt and scripts")

    for x in ["py","sh","txt","js","html","c","css"]:
        txt.add_pattern(f"*{x}")

    list_store = Gio.ListStore()
    list_store.append(filter_)
    list_store.append(txt)

    dialog.set_filters( list_store )

    dialog.set_modal(True)
    return dialog

def mesaj_button(body, heading, buttons=list):
    """for gtk.AlertDialog use set_message
    # and set_description
    # add_buttons(["1","2"] you can catch the
    # repsone with list item id"""
    dialog = Adw.AlertDialog(heading_use_markup=True,
        body_use_markup=True)

    for id_, button in enumerate(buttons):
        # 1 > blue 2 > red 0 > normal
        buton_info, color = button.split(":")
        dialog.add_response(f"{id_}", buton_info)
        dialog.set_response_appearance(f"{id_}", color)

    dialog.set_heading(heading)
    dialog.set_body(body)
    return dialog

def mesaj(msj, pencere=None, style=None):
    """run a message dialog for given text
    !will be updated later on... """

    alert = Adw.AlertDialog()
    try:
        heading, body = msj.split("\n")
        alert.set_heading(heading)
        alert.set_body(body)
    except TypeError:
        alert.set_body(msj)

   # alert.set_content_height(500)
    alert.add_response("OK", "OK")
    pencere.set_sensitive(False)

    def dialog_(widget, response_id):
        response_id = widget.choose_finish(response_id)
        if response_id == "OK":
    #        print(widget, response_id)
    #        widget.destroy()
            pencere.set_sensitive(True)

    alert.choose(pencere, None, dialog_)

    if style:
        style.add_custom_styling(alert)
    else:
        pencere.add_custom_styling(alert)

def hata(msj, wikieditor):
    """
    returns custom error message for wikitext
    """
    buffer = wikieditor.current_buffer

   # pixbuf =  GdkPixbuf.Pixbuf.new_from_file_at_size("gtk-cancel.png",128,128)
    iter_ = buffer.get_iter_at_offset(0)
    buffer.insert(iter_, "\n \n \n ")
   # print(dir(buffer))
   # buffer.insert_pixbuf(iter_, pixbuf)
    buffer.insert(iter_, msj.replace("\n","\n \n "))
    tag = buffer.create_tag( foreground="black",
            paragraph_background="#7F3731",
            right_margin=0,
            indent=50,
            left_margin=0,
            size_points=13.0,
            wrap_mode=gtk.WrapMode.WORD )

    start, end = buffer.get_bounds()
    buffer.apply_tag(tag, start, end)
    wikieditor.current_editor.set_editable(False)
    wikieditor.current_editor.set_show_line_numbers(False)
    parent =  wikieditor.current_editor.get_parent()
    parent.set_sensitive(False)
    buffer.set_modified(False)
