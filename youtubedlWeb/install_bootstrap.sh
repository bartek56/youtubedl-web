#!/bin/bash

printf " ----- Bootstrap and clockpicker ----- \n"
bootstrapExist=$(ls ./static/ | grep bootstrap | wc -l)
if [ $bootstrapExist -gt 0 ]; then
    printf "Boostrap for youtubedl is installed \n"
else
    cd ./static
    wget https://github.com/twbs/bootstrap/releases/download/v5.0.0-beta1/bootstrap-5.0.0-beta1-dist.zip
    unzip bootstrap-5.0.0-beta1-dist.zip
    mv bootstrap-5.0.0-beta1-dist bootstrap-5.0.0 --force
    rm bootstrap-5.0.0-beta1-dist.zip
    # clock picker
    wget https://github.com/weareoutman/clockpicker/archive/refs/tags/v0.0.7.zip
    unzip v0.0.7.zip
    mv clockpicker-0.0.7 clockpicker
    rm v0.0.7.zip
    cd ..
fi
