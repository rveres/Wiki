import webapp2
import jinja2

import logging

from google.appengine.ext import db

import os
import re
'[undisclosed]'
'[undisclosed]'
import logging
import time

from google.appengine.api import memcache
from google.appengine.ext import db

from utility import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class WikiHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', '[undisclosed]')

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

	def notfound(self):
		self.error(404)
		self.write("<h1>404: Not Found</h1>That page doesn't exist!")

def users_key(group = 'default'):
	return db.Key.from_path('users', group)

class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid)

	@classmethod
	def by_name(cls, name):
		u = User.all().filter('name =', name).get()
		return u

	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = make_pw_hash(name, pw)
		return User(name = name,
					pw_hash = pw_hash,
					email = email)

	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u

class Content(db.Model):
	content = db.TextProperty(required = True)
	path = db.StringProperty(required = True)
	author = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

def requested_page(update, path, new_content = None, new_author = None):
	content_key = str(path)
	author_key = content_key + ':author'
	page_content = memcache.get(content_key)
	page_author = memcache.get(author_key)
	if update:
		page_content = new_content
		page_author = new_author
		memcache.set(content_key, new_content)
		memcache.set(author_key, new_author)
		return
	elif page_content == None:
		logging.error("DB QUERY PAGE")
		page_cursor = db.GqlQuery("SELECT * FROM Content WHERE path = :1 ORDER BY created DESC LIMIT 1",path)
		page_key = page_cursor.get()
		if page_key:
			page_content = page_key.content
			page_author = page_key.author
		else:
			page_content = ""
			page_author = None
		memcache.set(content_key, page_content)
		memcache.set(author_key, page_author)

	results = {'content' : page_content, 'author' : page_author} 
	return results

def cached_history_page(update, path):
	history_key = str(path) + '/history'
	history_list = memcache.get(history_key)
	if update or history_list == None:
		logging.error("DB QUERY HISTORY")
		history_list = db.GqlQuery("SELECT * FROM Content WHERE path = :1 ORDER BY created DESC LIMIT 10",path)
		history_list = list(history_list)
		memcache.set(history_key, history_list)

	return history_list


class SignUp(WikiHandler):
	def get(self):
		next_url = self.request.headers.get('referer', '/')
		if next_url == 'http://wiki-152802.appspot.com/login':
			next_url = '/'
		self.render("signup_form.html", next_url = next_url)

	def post(self):
		have_error = False

		next_url = str(self.request.get('next_url'))
		if not next_url or next_url.startswith('/login'):
			next_url = '/'

		self.username = self.request.get('username')
		self.password = self.request.get('password')
		self.verify = self.request.get('verify')
		self.email = self.request.get('email')

		params = dict(username = self.username, email = self.email)

		if not valid_username(self.username):
			params['error_username'] = "That's not a valid username."
			have_error = True

		if not valid_password(self.password):
			params['error_password'] = "That wasn't a valid password."
			have_error = True
		elif self.password != self.verify:
			params['error_verify'] = "Your passwords didn't match."
			have_error = True

		if not valid_email(self.email):
			params['error_email'] = "That's not a valid email."
			have_error = True

		u = User.by_name(self.username)
		if u:
			params['error_exist'] = "That user already exists."
			have_error = True

		if have_error:
			self.render('signup_form.html', **params)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)
			self.redirect(next_url)

class Login(WikiHandler):
	def get(self):
		if self.user:
			self.redirect('/')

		next_url = self.request.headers.get('referer', '/')
		if next_url == 'http://wiki-152802.appspot.com/signup':
			next_url = '/'
		self.render('login_form.html', next_url = next_url)

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		next_url = str(self.request.get('next_url'))
		if not next_url or next_url.startswith('/signup'):
			next_url = '/'

		u = User.login(username, password)

		if u:
			self.login(u)
			self.redirect(next_url)
		else:
			error = "Invalid Login"
			self.render('login_form.html', error = error)

class Logout(WikiHandler):
	def get(self):
		next_url = self.request.headers.get('referer', '/')
		self.logout()
		self.redirect(next_url)

class WikiPage(WikiHandler):
	def get(self, path):
		edit_path = '/_edit' + path
		history_path = '/_history' + path

		v = self.request.get('v')
		match_key = None

		if v:
			if v.isdigit():
				logging.error("DB QUERY")
				match_key = Content.get_by_id(int(v))

				if not match_key:
					self.write('404. The page could not be found.')
					return
				else:
					match_content = match_key.content
					match_author = match_key.author

		else:
			match = requested_page(False, path)
			if match['content']:
				match_content = match['content']
				match_content = match_content.replace('\n','<br>')
				match_content = match_content.replace('+', ' ')
				match_author = match['author']
			elif not match['content']:
				self.redirect('/_edit' + path)
				return

		self.render('wiki_page.html', edit_path = edit_path, history_path = history_path, match_author = match_author, match_content = match_content)

class EditPage(WikiHandler):
	def get(self, path):
		history_path = '/_history' + path

		stored_page = None
		if not self.user:
			self.redirect('/login')
		else:
			v = self.request.get('v')
			match_key = None

			if v:
				if v.isdigit():
					logging.error("DB QUERY")
					match_key = Content.get_by_id(int(v))

					if not match_key:
						match = ""
					else:
						match_content = match_key.content
						match_author = match_key.author
			else:
				match = requested_page(False, path)

				if match['content'] == None or match['content'] == "":
					match_content = ""
					match_author = None
				else:
					match_content = match['content']
					match_author = match['author']

			self.render('edit_page.html', path = path, history_path = history_path, match_author = match_author, match_content = match_content)

	def post(self, path):
		if not self.user:
			self.error(404)
			self.redirect('/')
			return

		forward_path = self.request.get('path')
		updated_content = self.request.get('content')
		updated_author = '[undisclosed]'
		match = requested_page(False, path)
		if match == None:
				match = ""

		if not updated_content:
			self.redirect(forward_path)
		elif not match or match != updated_content:
			bwd_file = open("bwd_list.txt", "r")
			bwd_load_list = bwd_file.read().split(', ')

			for word in bwd_load_list:
				if word.lower() in updated_content.lower():
					logging.error("BWD_FOUND")
					bwd_file.close()
					self.redirect(forward_path)
					return
			
			bwd_file.close()
			
			p = Content(content = updated_content, path = forward_path, author = updated_author)
			p.put()
			logging.error("DB QUERY MOUNT")
			time.sleep(0.1)

			requested_page(True, forward_path, updated_content, updated_author)
			cached_history_page(True, forward_path)

		self.redirect(forward_path)

class HistoryPage(WikiHandler):
	def get(self, path):
		edit_path = '/_edit' + path
		view_path = path

		if not self.user:
			self.redirect('/login')
		else:
			stored_pages = cached_history_page(False, path)
			self.render('history_page.html', stored_pages = stored_pages, view_path = view_path, edit_path = edit_path)


PAGE_RE = '[undisclosed]'

app = webapp2.WSGIApplication([('/signup', SignUp),
								('/login', Login),
								('/logout', Logout),
								('/_edit' + PAGE_RE, EditPage),
								('/_history' + PAGE_RE, HistoryPage),
								(PAGE_RE, WikiPage),
								],
								debug = True)