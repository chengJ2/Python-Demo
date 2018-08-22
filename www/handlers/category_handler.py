#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
 category api handler

'''
import logging;logging.basicConfig(level=logging.INFO)

from coroweb import get, post

from models import Category

@get('/api/category')
def get_category():
	categorys = yield from Category.findAll('enable=?',[1])
	return dict(categorys=categorys)