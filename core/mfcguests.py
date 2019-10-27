class guest_client(WebSocketBaseClient):
	def handshake_ok(self): 
		self.joined_room=0
		self.websockmgr.gbot.add(self)
		self.ws=self.websockmgr.gbot.websockets[self.sock.fileno()]
		#self.ws.send("hello fcserver\n\0")
		#self.ws.send("1 0 0 20071025 0 guest:guest\n\0")
		self.ws_main.send("fcsws_20180422\n\0") # new MFC ws protocol 4/24/18
		self.ws_main.send("1 0 0 20071025 0 1/guest:guest\n\0")
		self.websockmgr.gcount=self.websockmgr.gcount+1
	def received_message (self,data):
		if self.joined_room == 1:
			return
		i=1
		data=str(data)
		while i==1:
			hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", data)
			if bool(hdr) == 0:
				cli_out ("ERROR: parse_response failed %s" % data)
				break
			msgtype = hdr.group(1)
			msg_len=int(msgtype[0:6])
			msgtype=int(msgtype[6:])
			Message=data[6:6+msg_len]
			Message = data[6:6+msg_len] # new MFC ws protocol 4/24/18
			Message=urllib.unquote(Message)

			if msgtype == 1:
				self.joinroom (self.ws)
			elif msgtype == 5:
				Message=Message[Message.find("{")+1:]
				dump=re.match(r'(\"lv\"):(?P<LEVEL>\d+),(\"nm\"):(?P<NAME>.+?),(\"sid\"):(?P<SID>\d+)', 
						Message)
				if bool(dump):
					guest_name=dump.group('NAME')
					self.Name=guest_name
					s_id=int(dump.group('SID'))
					self.websockmgr.g_sid[guest_name]=[self.ws, s_id]
			elif msgtype == 63:
				self.websockmgr.guest_conn += 1
				cli_out(fg.blue+"Joined \"%s\" room - guests added %d%s" 
					% (self.websockmgr.camgirl, self.websockmgr.guest_conn, attr.reset))
				self.joined_room = 1
			elif msgtype == 11:
				if self.Name in Message:
					try:
						self.ws.close()
						if enable_tor == 1:
							New_tor_id()
							time.sleep(1)
					except:
						cli_out(fg.red+"Error in closing connection"+attr.reset)
					pass
			#process next message
			data=data[6+msg_len:]
			if len(data) == 0:
				break
	def joinroom(self, ws):
		ws.send("51 0 0 %d 1 -\n\0" % (self.websockmgr.mchanid)); 

	def connection_closed(self):
		if self.Name==None:
			return
		try:
			del self.websockmgr.g_sid[self.Name]
		except KeyError:
			pass
		if self.joined_room == 1:
			self.websockmgr.gcount=self.websockmgr.gcount-1
			self.websockmgr.guest_conn -= 1
			cli_out("Removed guest %s from %s room (%d)\n" % 
				(self.Name, self.websockmgr.camgirl, self.websockmgr.guest_conn))
