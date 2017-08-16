#!/bin/bash

prefix=$1
repeated=$2
suffix=$3
maxlength=$4
guild=$5
auth=$6

s="${prefix}${repeated}"; while [ ${#s} -le ${maxlength} ]; do echo "${s}${suffix}"; s="${s}${repeated}"; done | xargs ./search.py $guild $auth "${prefix}${repeated}${suffix}.csv"
