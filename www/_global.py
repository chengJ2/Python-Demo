#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def _init():
	global _gb_dict
	_gb_dict = {}

def set_value(key,value):
	_gb_dict[key] = value

def get_value(key,defValue=None):
	try:
		return _gb_dict[key]
	except KeyError:
		return defValue
