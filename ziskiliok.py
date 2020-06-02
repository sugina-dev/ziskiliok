#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
from html import escape
import sqlite3

DB_STRING = 'data.sqlite3'

class Ziskiliok:
	@cherrypy.expose
	def index(self, **kwargs):
		lang = kwargs.get('lang')
		user = kwargs.get('user')
		content = kwargs.get('content')
		if lang and content:
			with sqlite3.connect(DB_STRING) as con:
				con.execute('INSERT INTO ziskiliok (lang, user, content) VALUES (?, ?, ?)', (lang, user, content.rstrip()))
			raise cherrypy.HTTPRedirect('.')
		else:
			def make_entry(lang, user, content, time):
				return '<div><span>' + user + ' - <time datetime="' + time + '">' + time + '</time></span><pre class="message" lang="' + lang + '">' + escape(content) + '</pre></div>'

			d = []
			d.append('''<!DOCTYPE html>
<html lang="zh-HK">
<head>
<title>日記錄</title>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>html {
padding: 0 1em;
}
body {
background-color: lightpink;
font-family: sans-serif;
margin: 0 auto;
max-width: 60em;
}
input, select, option, textarea {
background-color: lightblue;
border: 1px solid;
font-family: inherit;
}
textarea {
box-sizing: border-box;
height: 8em;
width: 100%;
padding: 0.5em;
}
input[type="submit"] {
padding: 4px 14px;
}
body > div {
border: 1px solid;
border-radius: 0.5em;
background-color: lightblue;
margin: 1em 0;
padding: 0 1em;
}
body > div > span {
color: #444;
display: block;
font-size: 80%;
margin: 1em 0;
text-align: right;
}
.message {
font-family: inherit;
line-height: 1.4;
margin: 1em 0;
white-space: pre-wrap;
}
.center {
text-align: center;
}
</style>
</head>
<body>
<h1>日記錄</h1>
<form>
<p>
<label>
語言代碼：
<select id="lang" name="lang" lang="en-HK">
<option value="cmn-HK">官話 (cmn-HK)</option>
<option value="yue-HK">粵語 (yue-HK)</option>
<option value="ja">日語 (ja)</option>
<option value="ko-KR">韓語 (ko-KR)</option>
<option value="en">英語 (en)</option>
<option value="de">德語 (de)</option>
</select>
</label>
</p>
<p>
<label>
用户：
<label><input type="radio" name="user" value="User1" checked> <span lang="en-HK">User1</span></label>
<label><input type="radio" name="user" value="User2"> <span lang="en-HK">User2</span></label>
</label>
</p>
<p><textarea type="text" name="content" minlength="180" required></textarea></p>
<p class="center"><input type="submit" value="Po 上"/></p>
</form>''')

			with sqlite3.connect(DB_STRING) as con:
				for lang, user, content, time in con.execute("SELECT lang, user, content, strftime('%Y-%m-%dT%H:%M:%fZ', time) FROM ziskiliok ORDER BY id DESC"):
					d.append(make_entry(lang, user, content, time))

			d.append('''</body>
<script>[...document.getElementsByTagName('time')].map(x => {
x.innerText = (new Date(x.dateTime)).toLocaleString('zh-CN', { hour12: false });
x.lang = 'zh-CN';
});
</script>
</html>''')

			return '\n'.join(d)

def setup_database():
	with sqlite3.connect(DB_STRING) as con:
		con.execute('''CREATE TABLE IF NOT EXISTS ziskiliok
( 'id' INTEGER PRIMARY KEY
, 'lang' TEXT NOT NULL
, 'user' TEXT NOT NULL
, 'content' TEXT NOT NULL
, 'time' TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);''')

if __name__ == '__main__':
	cherrypy.config.update({'server.socket_port': 3004})
	cherrypy.engine.subscribe('start', setup_database)
	cherrypy.quickstart(Ziskiliok())
