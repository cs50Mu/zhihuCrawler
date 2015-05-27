import os
import time
import urllib2
import json
from urllib import urlencode
from cookielib import LWPCookieJar
import sys
from lxml import html
reload(sys)
sys.setdefaultencoding('utf-8') 



class zhihuCrawler(object):
	
	def __init__(self, login_url, login_info, header):
		self.base_url = 'http://www.zhihu.com'
		self.login_url = login_url
		self.login_info = login_info
		self.header = header
		self.cookies = LWPCookieJar('cookies.jar')

		try:
			self.cookies.revert()
		#	print open(cookies.filename).read()
		except Exception,e:
			print 'First time to login, setting up cookies...'

		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		urllib2.install_opener(opener)
	
	def login(self):
		f = self.request(self.login_url, urlencode(self.login_info))
		j = json.loads(f)   # the response is in json format
		if int(j['r']) == 1:
			if 'captcha' in j['msg']:
				print '需要输入验证码'
				captcha = tree.find_class('js-captcha-img')[0]
				captcha_url = 'http://www.zhihu.com' + captcha.attrib['src']
				print captcha_url
				with open('captcha.gif', 'w') as f:
					ca = self.request(captcha_url)
					f.write(ca)
				captcha = raw_input('请输入验证码： ')
				login_info['captcha'] = captcha
				f = self.request(self.login_url, urlencode(login_info))
				j = json.loads(f)
				if int(j['r']) == 0:
					self.cookies.save()
					print '登录成功～'
					return True
				else:
					print '登录失败'
					return False
			else:
				print '登录失败, 错误信息： %s' % j['msg'].items()[0][1]
		else:
			print 'login success!'
			self.cookies.save()
			return True

	def getClipList(self):
		clip_dict = {}
		clip_url = self.base_url + '/collections/mine'
		f = self.request(clip_url)
		tree = html.fromstring(f)
		clips = tree.find_class('zm-item-title')
		for clip in clips:
			clip_info = clip[0]
			url = self.base_url + clip_info.get('href')
			clip_dict[clip_info.text] = url
		return clip_dict

	def request(self, url, data=None):
		req = urllib2.Request(url,data=data, headers=self.header)
		f = urllib2.urlopen(req).read()
		return f

	def processOnePage(self, clip_url):
		f = self.request(clip_url)
		tree = html.fromstring(f)
		articles = tree.find_class('zm-item')
		article_dict = {}
		for article in articles:
			if len(article) > 1:
				title = article[0][0].text.replace('/', '-').replace('\\', '-')
				content = article[1][0][4][0].text
				if not content:
					content = ''
				article_dict[title] = [content]
			else:
				content = article[0][0][4][0].text
				if not content:
					content = ''
				article_dict[title].append(content)
		for a,c in article_dict.items():
			with open(a+'.html','w') as f:
				f.write('\n\n'.join(c))

	def processUseranswer(self, clip_url):
		f = self.request(clip_url)
		tree = html.fromstring(f)
		articles = tree.find_class('zm-item')
		article_dict = {}
		for article in articles:
			if len(article) > 1:
				title = article[0][0].text.replace('/', '-').replace('\\', '-')
				if len(title) > 40:
					title = title[:40]  # handle filename too long problem
				content = article[1][4][0].text
				if not content:
					content = ''
				article_dict[title] = [content]
			else:
				content = article[0][0][4][0].text
				if not content:
					content = ''
				article_dict[title].append(content)
		for a,c in article_dict.items():
			with open(a+'.html','w') as f:
				f.write('\n\n'.join(c))

	def processClip(self, clip_url):
		f = self.request(clip_url)
		tree = html.fromstring(f)
		more = tree.find_class('zm-invite-pager')
		if not more:
			print 'There is only one page for this clip'
			self.processOnePage(clip_url)
		else:
			page_num = int(more[0][-2][0].text)
			print 'There are %d pages for this clip' % page_num
			for i in xrange(1, page_num+1):
				print 'Processing number %d page...' % i
				self.processOnePage(clip_url + '?page=%d' % i)

	def getAlluserAns(self, ans_url):
		f = self.request(ans_url)
		tree = html.fromstring(f)
		more = tree.find_class('zm-invite-pager')
		if not more:
			print 'There is only one page for this clip'
			self.processUseranswer(ans_url)
		else:
			page_num = int(more[0][-2][0].text)
			print 'There are %d pages for this clip' % page_num
			for i in xrange(1, page_num+1):
				print 'Processing number %d page...' % i
				self.processUseranswer(ans_url + '?page=%d' % i)

#	def getAllanswers(self, uid):
#		ans_url = '{base}people/{uid}/answers'.format(base=self.base_url, uid=uid)
		



		
if __name__ == '__main__':

	login_url = 'http://www.zhihu.com/login'

	login_info = {
			'email' : 'linuxfish.exe@gmail.com',
			'password' : 'ILoveLinux',
			'_xsrf' : 'affb0220344ed0bf90c5b0083e1c80dc'
			}

	#login_info = {
	#		'email' : '474255758@qq.com',
	#		'password' : 'muchun0221',
	#		'_xsrf' : 'affb0220344ed0bf90c5b0083e1c80dc'
	#		}

	header = {
		'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
		'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'X-Requested-With' : 'XMLHttpRequest',
		'Referer' : 'http://www.zhihu.com/'
		}
	zhihu = zhihuCrawler(login_url, login_info, header)
	if zhihu.login():
#		d = zhihu.getClipList()
#		for clip_name, clip_url in d.items():
#			print 'Processing clip: %s' % clip_name
#			os.mkdir(clip_name)
#			os.chdir(clip_name)
#			zhihu.processClip(clip_url)
#			os.chdir('../')


		uid = raw_input('Please input the user id: ')
		os.mkdir(uid)
		os.chdir(uid)
		ans_url = '{base}/people/{uid}/answers'.format(base=zhihu.base_url, uid=uid)
		print ans_url
		zhihu.getAlluserAns(ans_url)
