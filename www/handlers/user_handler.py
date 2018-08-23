#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
 user api handler

'''
import logging;logging.basicConfig(level=logging.INFO)

from coroweb import get, post

from apis import APIError,APIValueError, APIResourceNotFoundError,APIPermissionError

from models import User, next_id,Follow,Fans

from aiohttp import web

import re,os,json,time,hashlib

from handler import get_page_index,user2cookie
from comm import COOKIE_NAME,_RE_SHA1,_RE_EMAIL,Page

@get('/api/allusers')
def index(request):
	users = yield from User.findAll()
	#users = yield from User.findAll('id=?',[2],orderBy='created_at desc')
	#users = yield from User.findAll('id>? and uadmin=?',[2,0],orderBy='created_at desc')
	return {
		'__template__': 'test.html',
		'users': users
	}

@get('/user/{id}')
def get_user(id):
	user = yield from User.find(id)
	return {
		'__template__': 'user/user.html',
		'user': user
	}

@get('/signout')
def signout(request):
	request.__user__ = None
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME,'-deleted-',max_age=0,httponly=True)
	logging.info('user signed out.')
	return r

@get('/signin')
def signin():
	return {
		'__template__': 'user/signin.html'
	}

@get('/register')
def register():
	return {
		'__template__': 'user/register.html'
	}

@post('/api/users')
def api_register_user(*,email,phone,name,passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('password')
	users = yield from User.findAll('email=?',[email])
	if len(users) > 0:
		raise APIError('register:failed', 'email', 'Email is already in use.')
	uid = next_id()
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid,name=name.strip(),email=email,phone=phone,passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),admin=0,status=1,avatar='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	yield from user.save()
	r = web.Response()
	r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@post('/api/authenticate')
def authenticate(*,email,passwd):
	if not email or not passwd:
		raise APIValueError('email', 'Email or password can not be empty')
	users = yield from User.findAll('email=? or phone=?',[email,email])
	if len(users) == 0:
		raise APIValueError('email', 'Email not exist.')
	users = yield from User.findAll('(email=? or phone=?) and status=?',[email,email,1])
	if len(users) == 0:
		raise APIValueError('banned', 'You have been banned.')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Error password.')
	r = web.Response()
	r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=84600,httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@get('/manage/follows')
def followedUser(request,*,page=1):
	if request.__user__ is not None:
		user_Id = request.__user__.id
		# sql = " ".join(['SELECT u.*,f.followed_user FROM follow f ',
		# 				'LEFT JOIN users u ON f.followed_user = u.id',
		# 				"WHERE f.user_id ='%s'"%user_Id,
		# 				"and f.status=1"])
		# follows = yield from Follow.unionSelect(sql)

		# sql = " ".join(['SELECT f1.status AS status1,f2.status AS status2 FROM follow f1,follow f2',
		# 		'WHERE f1.user_id = f2.followed_user AND f1.followed_user = f2.user_id',
		# 		"AND f1.user_id = '%s'"%user_Id])
		# follow_relation  = yield from Follow.unionSelect(sql)

		sql = " ".join(['SELECT u.*,f1.user_id,f1.followed_user,f1.status AS status1,f2.status AS status2 FROM follow f1',
				'LEFT JOIN follow f2 ON f1.user_id = f2.followed_user AND f1.followed_user = f2.user_id',
				'LEFT JOIN users u ON f1.followed_user = u.id',
				"WHERE f1.user_id = '%s'"%user_Id])
		follows = yield from Follow.unionSelect(sql)

		#newFollows = []

		for index,follow in enumerate(follows):
			follow.index = index
			follow.avatar_url = follow.avatar
			follow.cf_count = 1
			follow.cf_info = 'Python'

			if follow.status1 == '1' and follow.status2 == '1':
				relation_status = 2
				is_followed = True
				is_following = True
			elif follow.status1 == '0' and follow.status2 == '1':
				relation_status = 1
				is_followed = False
				is_following = True
			elif follow.status1 == '1' and (follow.status2 == '0' or follow.status2 == None):
				relation_status = 1
				is_followed = True
				is_following = False
			else:
				relation_status = 0
				is_followed = False
				is_following = False

			follow.is_followed = is_followed
			follow.is_following = is_following
			follow.relation_status = relation_status

			# newFollow = {}
			# newFollow['index']= index
			# newFollow['avatar_url'] = follow.avatar
			# newFollow['is_followed'] = is_followed
			# newFollow['is_following'] = is_following
			# newFollow['relation_status'] = relation_status
			# newFollows.append(newFollow)

		return {
			'__template__': 'user/follow.html',
			'page':page,
			'follows': follows
		}
		#return dict(data=newFollows)
	else:
		return web.HTTPFound('/signin')


def relation_status(user_Id):
	sql = " ".join(['SELECT f1.status AS status1,f2.status AS status2 FROM follow f1,follow f2',
				'WHERE f1.user_id = f2.followed_user AND f1.followed_user = f2.user_id'
				"AND f1.user_id = '%s'"%user_Id])
	follow = yield from Follow.unionSelect(sql)
	print (follow)
	return follow

@get('/manage/fans')
def followerUser(request,*,page=1):
	if request.__user__ is not None:
		user_Id = request.__user__.id
		sql = " ".join(['SELECT u.*,f.status AS fstatus FROM fans f ',
						'LEFT JOIN users u ON f.follower_user = u.id',
						"WHERE f.user_id ='%s'"%user_Id,
						"and f.status=1"])
		fans = yield from Fans.unionSelect(sql)
		return {
			'__template__': 'user/fans.html',
			'page':page,
			'fans': fans
		}
	else:
		return web.HTTPFound('/signin')


@post('/api/follow/')
def followUser(request,*,page='1',followed_user):
	follow = Follow(user_Id=request.__user__.id,followed_user=followed_user,status=1)
	yield from follow.save()

	fans = Fans(user_Id=followed_user,follower_user=request.__user__.id,status=1)
	yield from fans.save()

	return dict(follow=follow)

@post('/api/fans/')
def fansUser(*,follower_user):
	fans = Fans(user_Id=__user__.id,follower_user=follower_user)
	yield from fans.save()
	return dict(fans=fans)