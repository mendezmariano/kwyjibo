#!/bin/bash

echo "Hola mundooooo!!!"

TMP=archivo_temporal.txt
echo "Linea loca" > $TMP
echo "Linea cuerda" >> $TMP

grep 'loca' $TMP

exit($?)
