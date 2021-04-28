#!/usr/bin/bash

# normalize vocabs file prior to LM adaptabion
# lexicon file must contain only 1 word per line

# Usage
# bash $0 input-lexicon-file

inputtxt=$1
outputtxt=$(dirname $inputtxt)/vocab.txt

# 1) get first text column from textfile, 
# 2) remove lines starting with special characters, e.g. @,#,$,%,etc 
# 3) remove special characters within the words, eg There's -> Theres
# 4) remove duplicates
cat $inputtxt | cut -d ' ' -f1 | sed '/^[[:alpha:]]/!d' |  sed 's/[^a-z A-Z]//g' | uniq -u > $outputtxt

