#!/usr/bin/env bash

function set_title(){
    echo -en "\033]2;$@\007"
}
