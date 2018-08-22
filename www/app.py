#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio,sys

from aiohttp import web

sys.path.append('../')

from conf.config import configs

import orm

import logging;logging.basicConfig(level=logging.INFO)

from coroweb import add_routes, add_static

from factory import logger_factory,auth_factory,response_factory
from handlers.handler import _USER_HANDLER,_BLOG_HANDLER,_COMMENT_HANDLER,_CATEGORY_HANDLER
from comm import datetime_filter,init_jinja2

@asyncio.coroutine
def init(loop):
	yield from orm.create_pool(loop = loop,**configs.db)
	app = web.Application(loop = loop,
		middlewares=[
			logger_factory,
			auth_factory,
			response_factory])
	init_jinja2(app,filters=dict(datetime=datetime_filter))
	add_routes(app, _USER_HANDLER)
	add_routes(app, _BLOG_HANDLER)
	add_routes(app, _COMMENT_HANDLER)
	add_routes(app, _CATEGORY_HANDLER)
	add_static(app)
	srv = yield from loop.create_server(app.make_handler(),configs.server.host,configs.server.port)
	logging.info('Server started at %s:%s...' %(configs.server.host,configs.server.port))
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()