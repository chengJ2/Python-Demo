#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' 
Models for user, blog, comment. 
''' 

__author__ = 'Sandy Cheng'

import time,uuid

import orm

from orm import Model,StringField,BooleanField,FloatField,TextField

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
	__table__ = 'users'
	
	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	email = StringField(ddl='varchar(150)')
	phone = StringField(ddl='varchar(11)')
	passwd = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	avatar = StringField(ddl='varchar(128)')
	url = StringField(ddl='varchar(128)')
	status = StringField(ddl='varchar(2)')
	created_at = FloatField(default=time.time)

class Follow(Model):
	__table__ = 'follow'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	user_Id = StringField(ddl='varchar(50)')
	followed_user = StringField(ddl='varchar(50)')
	status = StringField(ddl='varchar(2)')
	created_at = FloatField(default=time.time)

class Fans(Model):
	__table__ = 'fans'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	user_Id = StringField(ddl='varchar(50)')
	follower_user = StringField(ddl='varchar(50)')
	status = StringField(ddl='varchar(2)')
	created_at = FloatField(default=time.time)

class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	title = StringField(ddl='varchar(150)')
	summary = StringField(ddl='varchar(200)')
	content = TextField()
	cover = StringField(ddl='varchar(50)')
	btype = StringField(ddl='varchar(2)')
	status = StringField(ddl='varchar(2)')
	status_color = StringField(ddl='varchar(10)')
	category_id = StringField(ddl='varchar(2)')
	commentState = StringField(ddl='varchar(2)')
	created_at = FloatField(default=time.time)

class Comment(Model):
	__table__ = 'comments'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	blog_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	content = TextField()
	created_at = FloatField(default=time.time)

class Commentslist(Model):

	__table__ = 'commentslist'
	
	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	comment_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	content = TextField()
	created_at = FloatField(default=time.time)

class Category(Model):
	__table__ = 'category'

	id = StringField(primary_key=True, ddl='int')
	name_CH = StringField(ddl='varchar(50)')
	name_EN = StringField(ddl='varchar(120)')
	enable = StringField(ddl='varchar(2)')