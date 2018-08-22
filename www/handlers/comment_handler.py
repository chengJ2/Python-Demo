#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
 comment api handler

'''

from apis import APIError,APIValueError,APIResourceNotFoundError,APIPermissionError

from coroweb import get, post
from handler import get_page_index

from models import Blog,Comment,Commentslist

from comm import Page

from aiohttp import web

@get('/manage/comments')
def manage_comments(request,*,page='1'):
	user = request.__user__
	if user is not None: 
		return {
			'__template__': 'comment/manage_comments.html',
			'page_index': get_page_index(page)
		}
	else:
		return web.HTTPFound('/')

@post('/api/create/comments')
def api_create_comment(request,*,blog_id,content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	blog = yield from Blog.find(blog_id)
	print ("blog--------->" + blog.id)
	if blog is None:
		raise APIResourceNotFoundError('Blog')
	if blog is not None and blog.commentState == '0':
		raise APIValueError('prohibiting', '该文章已禁止评论.')
	comment = Comment(blog_id=blog_id, user_id=user.id, content=content.strip())
	yield from comment.save()
	return comment

@get('/api/comments')
def api_comments(request,*, page='1'):
	page_index = get_page_index(page)
	num = yield from Blog.findNumber('count(id)','`status`=?',[1])
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, comments=())
	#comments = yield from Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	sql = " ".join(['SELECT b.*,COUNT(c.blog_id) AS commentsNum FROM  `blogs` b',
					'LEFT JOIN comments c ON b.id = c.blog_id',
					"WHERE b.`status` = 1 AND b.`user_id`='%s'"%request.__user__.id,
					'GROUP BY b.`id`',
					'ORDER BY b.`created_at` DESC',
					'LIMIT %s,%s'%(p.offset, p.limit)])
	comments = yield from Comment.unionSelect(sql)
	if comments:
		for c in comments:
			c.commentState = getCommentState(c.commentState)
	return dict(page=p, comments=comments)



@get('/api/blog/{blog_id}/comments')
def get_comments(blog_id, *, page='1'):
	page_index = get_page_index(page)
	num = yield from Comment.findNumber('count(id)','`blog_id`=?',[blog_id])
	page = Page(num, page_index)
	blog = yield from Blog.findAll('`id`=?',[blog_id])
	if num == 0:
		comments = []
	else:
		sql = " ".join(['SELECT c.* ,u.`name` AS user_name, u.`avatar` FROM `comments` c',
						'LEFT JOIN users u ON c.`user_id` = u.`id`',
						"WHERE c.`blog_id`='%s'"%blog_id,
						'GROUP BY c.`id`',
						'ORDER BY c.`created_at` DESC',
						'LIMIT %s,%s'%(page.offset, page.limit)])
		comments = yield from Comment.unionSelect(sql)
	return {
		'__template__': 'comment/blog_comments.html',
		'page':page,
		'blog':blog[0],
		'comments': comments
	}

@post('/api/comments/{id}/delete')
def delete_comments(request, *, id):
	comment = yield from Comment.find(id)
	yield from comment.remove()
	return dict(id=id)


@post('/api/commentList')
def api_commentList(request,*,commentId,content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	comment = Commentslist(comment_id=commentId, user_id=user.id, content=content.strip())
	yield from comment.save()
	return comment

@get('/api/commentList/{commentId}')
def api_commentsList(commentId):
	#commentsList = yield from Commentslist.findAll('comment_id=?',[commentId],orderBy='created_at desc')
	sql = " ".join(['SELECT co.* , u.`name`,u.`avatar` FROM commentslist co',
				'LEFT JOIN users u ON co.`user_id` = u.`id`',
				"WHERE co.comment_id = '%s'"%commentId,
				'ORDER BY co.`created_at` DESC'])
	commentsList = yield from Commentslist.unionSelect(sql)
	return dict(commentsList=commentsList)

def getCommentState(state):
	if state == "1":
		return "正常"
	else:
		return "禁止评论"