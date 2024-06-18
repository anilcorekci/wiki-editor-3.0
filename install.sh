#!/bin/bash
# ------------------------------------------------------------------------------
#   Copyright (c) @hitokiri. All rights reserved...
#   Licensed under the GPL 3 License.
# ------------------------------------------------------------------------------

files=(
    "$PWD/wiki-editor.desktop"
    "$PWD/Wiki-Editor"
    "$PWD/pyler/wiki-editor.png"
    "$PWD/etc_apparmor.d/Wiki-Editor"
)

root_files=(
    "/usr/share/applications/wiki-editor.desktop"
    "/usr/bin/Wiki-Editor"
    "/usr/share/icons/wiki-editor.png"
    "/etc/apparmor.d/Wiki-Editor"
)

function install_files {
    sed -i "9s|.*.|cd '$PWD'|" "$PWD/Wiki-Editor"

    chmod +x "$PWD/Wiki-Editor"
    chmod +x "$PWD/pyler/Wiki Editor"
    #installing dependencies
    sudo apt-get install -y  gir1.2-gtksource-5
    sudo apt-get install -y python3-gst-1.0

    i=-1
    for each in "${files[@]}"
    do
        let i+=1
        if [ -f  "$each" ]
        then
            sudo cp "$each"  "${root_files[$i]}"
            echo -e '\e[01;31msudo cp "'$each'"  "'${root_files[$i]}'"\e[00m'
        fi
    done

    # restart apparmor service
    sudo systemctl restart apparmor.service

}

function uninstall_files {
    for each in "${root_files[@]}"
    do
        if [ -f  "$each" ]
        then
            sudo rm -rf "$each"
            echo -e "\e[01;31msudo rm -rf '$each'\e[00m"
        fi
    done
}


function stamp {
    echo -e "
    # ------------------------------------------------------------------------------
    #   Copyright (c) @hitokiri. All rights reserved...
    #   Licensed under the GPL 3 License.
    #   2010 - 2024
    # ------------------------------------------------------------------------------

    1: To install Wiki Edior --install
    2: To uninstall Wiki Editor --uninstall

    "
}

while test $# -gt 0 ; do
  case $1 in
    --install )
      stamp|sed -n '1,7p'
      install_files
      exit $?
      ;;
    --uninstall )
      stamp|sed -n '1,7p'
      uninstall_files
      exit $?
      ;;
    * | --)
      shift
      break
      ;;
  esac
done

stamp
read option

case $option in
    1 | --install)
      install_files
      ;;
    2 | --uninstall)
      uninstall_files
      ;;
    * | -- )
      echo -e "\nUnknown Option.\n"
      shift
      ;;
esac
