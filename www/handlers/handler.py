#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Sandy Cheng'

' url handler '

import re,os,time,hashlib

from comm import _COOKIE_KEY

_USER_HANDLER = 'user_handler'
_BLOG_HANDLER = 'blog_handler'
_COMMENT_HANDLER = 'comment_handler'
_CATEGORY_HANDLER = 'category_handler'

def get_page_index(page_str):
	''
	p = 1
	try:
		p = int(page_str)
	except ValueError as e:
		pass
	if p < 1:
		p = 1
	return p

def user2cookie(user, max_age):
	'''
	Generate cookie str by user.
	'''
	# build cookie string by: id-expires-sha1
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)

def text2html(text):
	lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
	return ''.join(lines)


def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		return APIPermissionError()