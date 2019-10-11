#!/bin/bash

gcc -g -o test test.c -I src/interface/ -I src/ztools/ -Wl,-rpath=src -Lsrc -lfrotz
