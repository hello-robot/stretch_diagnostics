#!/bin/bash
pip3 uninstall hello-robot-stretch-production_tools

cd ~/
rm ~/git_token.txt
rm ~/.git*
rm ~/Pictures/*
rm ~/Downloads/*
rm ~/Documents/*
rm -rf ~/stretch_install
rm ~/.config/google-chrome/Default/
bleachbit --clean firefox.*

echo "Run 'rm -rf ~/repos/*' to empty the repos dir."


