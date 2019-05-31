#! /bin/sh
# Сохраняем в переменную BASEDIR путь к каталогу, где находится скрипт
BASEDIR=$(dirname $(realpath "$0"))

echo $BASEDIR

$BASEDIR/bin/python3 $BASEDIR/src/main.py start