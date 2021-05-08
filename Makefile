##*****************************
##* General Makefile commands *
##*****************************
##

export SHELL := /bin/bash
export PYTHON_INTERPRETER := $(shell ( ls ./venv/Scripts/python.exe ./venv/bin/python 2> /dev/null || echo python ) | head -n 1)
export BACKUP_FILENAME := ./backups/backup-$(shell date +'%Y%m%d-%H%M%S')

.DEFAULT_GOAL := help


include makefiles/Makefile.*


.PHONY: help
help:           ## show this help
	@sed -nE '/@sed/!s/##\s?//p' Makefile makefiles/*
