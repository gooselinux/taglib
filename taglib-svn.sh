#!/bin/sh

if [ -d taglib ]; then
    echo "Remove the \"taglib\" directory first !"
    exit 1
fi
svn export svn://anonsvn.kde.org/home/kde/trunk/kdesupport/taglib
tar -czf taglib-`date +%Y%m%d`.tar.gz taglib
rm -rf taglib
