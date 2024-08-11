@echo off
set jar_file=%1
set input_file=%2
java -jar %jar_file% -senseg -wordseg -postag -input %input_file%