#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
 blog api handler

'''
from apis import APIError,APIValueError, APIResourceNotFoundError,APIPermissionError

from coroweb import get, post

from models import Blog,Comment,Commentslist

from aiohttp import web

import markdown2

from handler import get_page_index,text2html,check_admin

from comm import Page

@get('/')
def index(*,page='1'):
	page_index = get_page_index(page)
	num = yield from Blog.findNumber('count(id)',"status=?",[1])
	page = Page(num,page_index)
	print ('page info：%s' % page)
	if page == 0:
		blogs = []
	else:
		#sql = 'SELECT b.* ,COUNT(c.blog_id) as commentsNum FROM  `blogs` b LEFT JOIN comments c ON b.id = c.blog_id GROUP BY b.`id` ORDER BY b.`created_at` DESC limit %s,%s'%(page.offset, page.limit)
		sql = ' '.join(['SELECT b.* ,u.`name` AS user_name,u.`avatar`,COUNT(c.blog_id) AS commentsNum ,ca.name_CH,ca.color FROM  `blogs` b',
						'LEFT JOIN users u ON b.`user_id` = u.`id`',
						'LEFT JOIN comments c ON b.id = c.blog_id',
						'LEFT JOIN category ca ON b.`category_id`=ca.id',
						'WHERE b.`status` = 1',
						'GROUP BY b.`id`',
						'ORDER BY b.`created_at` DESC',
						'LIMIT %s,%s'%(page.offset, page.limit)])
		blogs = yield from Blog.unionSelect(sql)
		for blog in blogs:
			if blog.cover:
				blog.display = "block"
			else :
				blog.display = "none"
		#blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
	return {
		'__template__': 'index.html',
		'page':page,
		'blogs': blogs
	}

@get('/blog/{id}')
def get_blog(id):
	#blog = yield from Blog.find(id)
	sql = " ".join(['SELECT b.* ,u.`name` AS user_name,u.`avatar`,u.`url` FROM  `blogs` b',
				'LEFT JOIN users u ON b.`user_id` = u.`id`',
				"WHERE b.id = '%s'"%id])
	blogs = yield from Blog.unionSelect(sql)

	sql2 = " ".join(['SELECT c.* ,u.`name` AS user_name,u.`avatar` FROM  `comments` c',
				'LEFT JOIN users u ON c.`user_id` = u.`id`',
				"WHERE c.blog_id = '%s'"%id,
				'ORDER BY c.`created_at` DESC'])

	#comments = yield from Comment.findAll('blog_id=?',[id],orderBy='created_at desc')
	comments = yield from Comment.unionSelect(sql2)

	for index,c in enumerate(comments):
		c.html_content = text2html(c.content)
		c.index = index
		c.commnetsNum = yield from Commentslist.findNumber('count(id)','comment_id=?',[c.id])

	if blogs:
		blog = blogs[0]
		blog.html_content = markdown2.markdown(blog.content)
		return {
			'__template__': 'blog/blog.html',
			'blog': blog,
			'comments': comments
		}

def api_commentsListNum(commentId):
	num = yield from Commentslist.findNumber('count(id)','comment_id=?',[commentId])
	return num

@get('/api/{commentId}/commentList/')
def api_commentsList(commentId):
	commentsList = yield from Commentslist.findAll('comment_id=?',[commentId],orderBy='created_at desc')
	return commentsList

@get('/user/blogs/create')
def user_create_blog():
	return {
		'__template__': 'blog/blog_edit.html',
		'id': '',
		'action': '/api/blogs'
	}

@get('/user/blogs/edit')
def user_edit_blog(*, id):
	return {
		'__template__': 'blog/blog_edit.html',
		'id': id,
		'action': '/api/blogs/%s' % id
	}


@get('/blogs/{userId}')
def user_blogs(request,*,userId,page='1'):
	if request.__user__ is not None:
		return {
			'__template__': 'blog/user_blogs.html',
			'userId':userId,
			'page_index': get_page_index(page)
		}
	else:
		return web.HTTPFound('/signin')

@get('/manage/blogs')
def manage_blogs(request,*,page='1'):
	return {
		'__template__': 'blog/user_blogs.html',
		'userId':request.__user__.id,
		'page_index': get_page_index(page)
	}

@post('/api/blogs')
def api_create_blog(request,*,title, summary, content, cover, category_id):
	#check_admin(request)
	if not title or not title.strip():
		raise APIValueError('title', 'title cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	blog = Blog(user_id=request.__user__.id,title=title.strip(),summary=summary.strip(),content=content.strip(),cover = cover.strip(),btype = 1,status = 2,commentState=1,category_id=category_id)
	yield from blog.save()
	return blog

@post('/api/blogs/{id}')
def api_update_blog(id,request,*,name, summary, content):
	#check_admin(request)
	blog = yield from Blog.find(id)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	blog.name = name.strip()
	blog.summary = summary.strip()
	blog.content = content.strip()
	yield from blog.update()
	return blog

@get('/api/blogs')
def api_blogs(request,*,userId, page='1'):
	page_index = get_page_index(page)
	num = yield from Blog.findNumber('count(id)','`user_id`=?',[userId])
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, blogs=())
	blogs = ()
	#blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	
	# sql = ' '.join(['SELECT b.* ,u.`name` AS user_name, u.`admin` FROM `blogs` b',
	# 					'LEFT JOIN users u ON b.`user_id` = u.`id`'
	# 					'GROUP BY b.`id`',
	# 					'ORDER BY b.`created_at` DESC',
	# 					'LIMIT %s,%s'%(p.offset, p.limit)])
	
	L = ['SELECT b.* ,u.`name` AS user_name, u.`admin`,COUNT(c.blog_id) AS commentsNum FROM `blogs` b',
		 'LEFT JOIN users u ON b.`user_id` = u.`id`',
		 'LEFT JOIN comments c ON b.id = c.blog_id',
		 "WHERE u.`id` = '%s'" % userId,
		 'GROUP BY b.`id`',
		 'ORDER BY b.`created_at` DESC',
		 'LIMIT %s,%s'%(p.offset, p.limit)]
	sql = ' '.join(L)
	blogs = yield from Blog.unionSelect(sql)
	for blog in blogs:
		blog.type = getBlogType(blog)
		blog.status = getBlogStatus(blog)
	return dict(page=p, blogs=blogs)

@get('/api/blogs/{id}')
def api_get_blog(*, id):
	blog = yield from Blog.find(id)
	return blog

@post('/api/blogs/{id}/delete')
def api_delete_blog(request, *, id):
	#check_admin(request)
	blog = yield from Blog.find(id)
	yield from blog.remove()
	return dict(id=id)

@post('/api/blogs/{id}/auditing/{auditing}')
def api_delete_blog(request, *, id,auditing):
	#check_admin(request)
	blog = yield from Blog.find(id)
	blog.status = auditing
	yield from blog.update()
	return dict(id=id)

@post('/api/blog/{id}/action')
def blog_action(request, *,id):
	blog = yield from Blog.find(id)
	print (blog)
	blog.commentState = 0
	yield from blog.update()
	return dict(id=id)

def getBlogType(blog):
	if blog.btype == "1":
		blog.type = "文章"
	elif blog.btype == "2":
		blog.type = "图集"
	elif blog.btype == "3":
		blog.type = "视频"
	else:
		blog.type = "文章"
	return blog.type

def getBlogStatus(blog):
	if blog.status == "1":
		blog.status = "已发表"
	elif blog.status == "2":
		blog.status = "审核中"
	elif blog.status == "3":
		blog.status = "修改审核中"
	elif blog.status == "4":
		blog.status = "草稿"
	elif blog.status == "5":
		blog.status = "未通过"
	elif blog.status == "6":
		blog.status = "已撤回"
	elif blog.status == "-1":
		blog.status = "已删除"
	else:
		blog.status = "审核中"
	return blog.status
