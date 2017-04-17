import os
import json
import datetime
import getpass, poplib
import getpass, os, imaplib, email
#from OpenSSL.crypto import load_certificate, FILETYPE_PEM
import feedparser

def MySystem(s):
	print(s)
	ret = os.system(s)
	if not ret ==0:
		assert(0)

#http://www.pythoner.com/414.html	
def getMsgs(servername, usernm, passwd):
	subject = 'Your SSL Certificate'
	conn = imaplib.IMAP4_SSL(servername)
	conn.login(usernm,passwd)
	conn.select('Inbox')
	typ, data = conn.search(None,'(UNSEEN SUBJECT "%s")' % subject)
	for num in data[0].split():
		typ, data = conn.fetch(num,'(RFC822)')
		msg = email.message_from_string(data[0][1])
		typ, data = conn.store(num,'-FLAGS','\\Seen')
		yield msg

def getAttachment(msg,check):
	for part in msg.walk():
		if part.get_content_type() == 'application/octet-stream':
			if check(part.get_filename()):
				return part.get_payload(decode=1)

if __name__ == 'x__main__':
	for msg in getMsgs():
		payload = getAttachment(msg,lambda x: x.endswith('.pem'))
		if not payload:
			continue
		try:
			cert = load_certificate(FILETYPE_PEM,payload)
		except:
			cert = None
		if cert:
			cn = cert.get_subject().commonName
			filename = "%s.pem" % cn
			if not os.path.exists(filename):
				open(filename,'w').write(payload)
				print "Writing to %s" % filename
			else:
				print "%s already exists" % filename
		
def do_wget(item):
	Opt=''
	if item.has_key('encoding'):
		Opt = Opt + ' --remote-encoding=%s'%(item['encoding'])
	#if item.has_key('dest_dir'):
	#	Opt = Opt + ' --directory-prefix=%s'%(item['dest_dir'])
	
	MySystem('wget %s %s'%(Opt, item['url']))

#http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001408244819215430d726128bf4fa78afe2890bec57736000	
def do_pop3(item):
	M = poplib.POP3(item['url'])
	M.user(item['user'])
	M.pass_(item['pass'])
	numMessages = len(M.list()[1])
	for i in range(numMessages):
		for j in M.retr(i+1)[1]:
			print j

def do_imap(item):
	for msg in getMsgs(item['url'], item['user'], item['pass']):
		print msg
		payload = getAttachment(msg,lambda x: x.endswith('.pem'))
		if not payload:
			continue
		try:
			cert = load_certificate(FILETYPE_PEM,payload)
		except:
			cert = None
		if cert:
			cn = cert.get_subject().commonName
			filename = "%s.pem" % cn
			if not os.path.exists(filename):
				open(filename,'w').write(payload)
				print "Writing to %s" % filename
			else:
				print "%s already exists" % filename
def do_rss(item):
	feed = feedparser.parse(item['url'])
	for rssItem in feed[ "items" ]:
		do_wget({'url':rssItem.link})
	
#http://stackoverflow.com/questions/311627/how-to-print-date-in-a-regular-format-in-python	
def Today():
	today = datetime.date.today()
	return today.strftime('%Y-%m-%d-%H-%M')
	
folder = 'data/%s'%Today()
if not os.path.isdir('data'):
	MySystem('mkdir %s'%('data'))
if not os.path.isdir(folder):	
	MySystem('mkdir %s'%folder)
s=open('config.json','r').read()
cfg = json.loads(s)
i=0
for item in cfg:
	print item['mode']
	sub_dir = '%s/%d'%(folder, i)
	if not os.path.isdir(sub_dir):
		MySystem('mkdir %s'%(sub_dir))
	#item['dest_dir'] = 
	cur_dir_bk = os.getcwd()
	os.chdir(sub_dir)
	locals()["do_%s"%item['mode']](item)
	i = i+1
	os.chdir(cur_dir_bk)
		