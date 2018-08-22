#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Configuration

Development environment
'''
__author__ = 'Sandy Cheng'

configs = {
	'debug':True,
	'server':{
		'host':'127.0.0.1',
		'port':9000
	},
	'db':{
		'host':'127.0.0.1',
		'port':3306,
		'user':'root',
		'password':'sandy',
		'db':'awesome'
	},
	'session':{
		'secret':'Awesome'
	}
}