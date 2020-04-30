from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
# from binascii import a2b_base64
import mysql.connector as conn
import os

mimeMap = {
  'html': 'text/html',
  'css': 'text/css',
  'js': 'text/javascript',
  'json': 'text/json',
  'txt': 'text/plain',
  'ico': 'image/x-icon',
  'jpg': 'image/jpg',
  'png': 'image/png'
}
myDB = conn.connect(
	user = 'root',
	host = 'localhost',
	password = 'sunny',
	database = 'rahul7'
)

myCrsr = myDB.cursor(dictionary = True)
rExt = re.compile(r'(?<=\.).+')

class Server(BaseHTTPRequestHandler):
	def _send_headers(self, ext):
		self.send_response(200)
		self.send_header('Content-Type', mimeMap[ext])
		self.end_headers()

	def do_GET(self):
		self.path = '/templates/index.html' if self.path == '/' else '/templates' + self.path
		ext = re.findall(rExt, self.path)[0]
		self._send_headers(ext)
		with open('.' + self.path, 'rb') as file:
			content = file.read()
		self.wfile.write(content)

	def do_POST(self):
		length = int(self.headers['Content-Length'])
		data = str(self.rfile.read(length), 'utf-8')
		print(data)
		req = json.loads(data)

		if req['TASK'] == 'load_chats':
			myCrsr.execute('SELECT * FROM CHATS;')
			req['chats'] = myCrsr.fetchall()
			# print(rows)

		elif req['TASK'] == 'save_chat':
			QUERY = 'INSERT INTO CHATS VALUES(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\');' % (
				req['NAME'], req['MSG'], req['TS'], req['TASK'], req['VOTERS']
			)
			print(QUERY)
			myCrsr.execute(QUERY)

		elif req['TASK'] == 'save_vote':
			QUERY = 'UPDATE CHATS SET VOTERS = \'%s\' WHERE TS = \'%s\';' % (
				req['VOTERS'], req['TS']
			)
			myCrsr.execute(QUERY)

		myDB.commit()
		self._send_response(json.dumps(req))

	def _send_response(self, resp):
		self._send_headers('txt')
		# print(resp)
		self.wfile.write(bytes(resp, 'utf-8'))

def startServer():
	serverAdd = ('', int(os.environ['PORT']))
	server = HTTPServer(serverAdd, Server)
	server.serve_forever()

startServer()

'''
MYSQL CREATE TABLE COMMAND:
CREATE TABLE CHATS ( NAME TEXT, MSG TEXT, TS CHAR(30), TASK TEXT, VOTERS TEXT )

'''