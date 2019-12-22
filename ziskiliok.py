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
		content = kwargs.get('content')
		if lang and content:
			with sqlite3.connect(DB_STRING) as con:
				con.execute('INSERT INTO ziskiliok (lang, content) VALUES (?, ?)', (lang, content.rstrip()))
			raise cherrypy.HTTPRedirect('.')
		else:
			def make_entry(lang, content, time):
				return '<div><time datetime="' + time + '">' + time + '</time><pre class="message" lang="' + lang + '">' + escape(content) + '</pre></div>'

			d = []
			d.append('''<!DOCTYPE html>
<html>
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
body > div > time {
color: #444;
display: block;
font-size: 80%;
margin: 1em 0;
text-align: right;
}
.message {
font-family: inherit;
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
<select id="lang" name="lang">
<option value="zh-Hant-HK-x-shn">漢語-繁體中文-湫霧市 (zh-Hant-HK-x-shn)</option>
<option value="zh-Hans-HK-x-shn">漢語-簡體中文-湫霧市 (zh-Hans-HK-x-shn)</option>
<option value="cmn">普通話 (cmn)</option>
<option value="yue">粵語 (yue)</option>
<option value="ja-Jpan-JP">日語-日文-日本 (ja-Jpan-JP)</option>
<option value="ko-KR">韓國語-韓國 (ko-KR)</option>
<option value="vi-Hani-VN">越南語-喃字-越南 (vi-Hani-VN)</option>
<option value="en-HK">英語-香港 (en-HK)</option>
<option value="de">德語 (de)</option>
<option value="ga">愛爾蘭語 (ga)</option>
<option value="nb">書面挪威語 (nb)</option>
<option value="nn">新挪威語 (nn)</option>
</select>
</label>
</p>
<textarea type="text" name="content" minlength="40" required></textarea>
<p class="center"><input type="submit" value="Po 上"/></p>
</form>''')

			with sqlite3.connect(DB_STRING) as con:
				for lang, content, time in con.execute("SELECT lang, content, strftime('%Y-%m-%dT%H:%M:%fZ', time) FROM ziskiliok ORDER BY id DESC"):
					d.append(make_entry(lang, content, time))

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
, 'content' TEXT NOT NULL
, 'time' TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);''')

if __name__ == '__main__':
	cherrypy.config.update({'server.socket_port': 3004})
	cherrypy.engine.subscribe('start', setup_database)
	cherrypy.quickstart(Ziskiliok())
