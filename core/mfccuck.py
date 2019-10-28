from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
import collections
from core.database import Database
from core.timezone import *
from core.cmn  import *
import time
import traceback
import threading
import json
import sys
import os
import random
import re
import urllib
import math


cg_bans={}

def main_keep_alive(web_sock):
        print "Starting Keep alive for MFCCUCKmgr\n"
	while web_sock.is_running == 1:
		#s_time=(math.floor(10 * random.random()) + 10)
		time.sleep(8);
		try:
       			for ws in web_sock.websockets.itervalues():
				if not ws.terminated:
					ws.send("0 0 0 0 0 -\n\0")
		except:
			pass
main_session = WebSocketManager()
main_session.start()
main_session.is_running=1
main_ka_thr=threading.Thread(target=main_keep_alive, args=[main_session])
main_ka_thr.setDaemon(True)
main_ka_thr.start()

online_camgirls={}

current_month=get_date_in_PT_TZ().strftime("%B")
current_year=get_date_in_PT_TZ().strftime("%Y")
gindex=1

def connect_xchat_server (camgirl, uid):
        cli_out("Connecting to Chat Server... :  "+camgirl)
	host = get_chat_host()
	try:
	       	client = MFC(host)
	except:
		print "MFC session error"
		return
	client.cs = 0
	client.camgirl=camgirl
	client.xchat_server=host
        client.mid_camgirl=uid
	client.Name=None
	try:
		client.connect ()
	except:
		e, t, tb = sys.exc_info()
		cli_out(fg.red+"Error: Could not able connect to \"%s\" : %s%s\n" % (camgirl, t, attr.reset))
		del client
		client=None
	return client



def end_session(uid):
	for session in client:
		if uid == session.mid_camgirl:
			client.remove(session)
			session.exit_session=1
			session.session_IO=0
			try:
				session.ws_main.send("98 0 0 0 0 -\n\0")
			except:
				pass

			try:
				session.ws_main.close()
			except:
				pass
			cli_out(fg.green+"%s went offline. Closing the session%s" 
				%(session.camgirl, attr.reset))
			time.sleep(0.1)
			del session
			return 1
	return 0

class MFC(WebSocketBaseClient):
	def handshake_ok(self): 
		global gindex
		self.gbot=None
		self.guest_conn = 0
		self.new_camgirl=0
		self.Incomplete_Buf=""
		self.joined=0
		self.cs=0
		self.room_count=0
		main_session.add(self)
		self.ws_main=main_session.websockets[self.sock.fileno()]
		self.mchanid = 0
		self.exit_session=0
		self.basics = 0
		self.prem = 0
		self.total_tips = 0
		self.tippers={}
		self.gbot_ka_thr=None
		self.index=gindex
		self.last_banned_member=""
		self.state="OFFLINE"
		self.cam_state=-1
		self.cam_srv=0
		self.m_index=0
		self.message_Q=collections.deque(maxlen=25)
		gindex += 1
		self.reconnect=0
		self.sess_id=0
		self.user_level=0
		self.memberuid=0
		self.gcount=0
		self.members = {}
		self.g_sid={}
		self.rank=0
		self.guests_count=0
		self.spam=0
		self.session_IO=0
		self.connected_on=get_date_in_PT_TZ().strftime("%H:%M %b %d,%Y")+" PT"
                '''
		info=db_getvaluelookup(db_camgirls, db_wl, str(self.camgirl));
		if info != None:
			self.mid_camgirl=int(info[1])

                '''
		self.start = int(time.time())

		self.ws_main.send("fcsws_20180422\n\0")
		self.ws_main.send("1 0 0 20071025 0 1/guest:guest\n\0")
		self.gcount=self.gcount+1
                '''
		#self.timer_join = Timer(180, room_join_timer_expiry, [self])
		#self.timer_join.start()
                '''

	def close_session(self):
		try:
			self.exit_session=1
			self.session_IO=0
			self.ws_main.send("98 0 0 0 0 -\n\0")
			self.ws_main.close()
#			try:
#				self.timer_join.cancel()
#			except:
#				pass
			client.remove(self)
		except:
			pass

	def connection_remove_and_reconn(self):
		try:
			self.exit_session=0
			self.session_IO=0
			self.ws_main.send("98 0 0 0 0 -\n\0")
			self.ws_main.close()
		except:
			pass

        def closed(self, code, reason):
		global client
                print(("Closed down", code, reason))
		cli_out(fg.green+"Connection to \"%s\" closed%s" % (self.camgirl, attr.reset))
		if self.Name!=None:
			del self.g_sid[self.Name]
		self.gcount=self.gcount-1
		self.guest_conn=self.guest_conn-1
#		try:
#			self.timer_join.cancel()
#		except:
#			pass
		now = int(time.time())
		self.guests_remove (-1)
		self.session_IO=0
		if self.gbot_ka_thr != None:
			self.gbot.close_all()
			self.gbot.stop()
			self.gbot_ka=0
		time.sleep(0.3)
		if self.exit_session == 0:
			cli_out(fg.green+"Re-Connecting to %s ... %s" % (self.camgirl, attr.reset))
			host = get_chat_host()
			try:
				session = MFC(host)
                                session.guest_name=None
				session.xchat_server=host
				session.camgirl=self.camgirl
				session.mid_camgirl=self.mid_camgirl
				session.connect ()
				client.append(session)
			except:
				e, t, tb = sys.exc_info()
				cli_out(fg.red+"Could not able to re-connect to \"%s\": \"%s\"%s" 
					% (self.camgirl, t, attr.reset))
		try:
			client.remove(self)
		except ValueError:
			pass
		del self

	def run_guest_cli_keep_alive(self):
		while self.gbot_ka == 1:
			s_time=(math.floor(10 * random.random()) + 10)
			time.sleep(s_time);
			try:
				for ws in self.gbot.websockets.itervalues():
					if not ws.terminated:
						try:	
							ws.send("0 0 0 0 0 -\n\0")
						except:
							e, t, tb = sys.exc_info()
							print("Closing guest session to %s(%d) %s" 
								% (self.camgirl, self.index, t))
							ws.close()
			except:
				pass
	def __del__(self):
		class_name = self.__class__.__name__
		pass

	def cli_out (self, f_arg, *argv):
		if self.session_IO == 0:
			return
		msg=f_arg
		for arg in argv:
			msg=msg+arg
		print msg

	def tip_msg(self, m):
		tipmsg=self.do_process_json_message(m)
		tokens = tipmsg['tokens']
		userid = str(tipmsg['u'][1])
		flags = tipmsg['flags']

		if (flags & 4096):
			member = "Anonymous"
		else:
			member = tipmsg['u'][2]

		#tipnote=""
		is_tipnote=0
		if (flags & 32768):
			#tipnote = ": "+"'"+tipmsg['msg']+"'"
			is_tipnote=1
		#hidden
		if tokens == 0:
			if is_tipnote == 1:
				tokens = 5
			else:
				tokens = 1

		self.total_tips += tokens
		try:
			tips=self.tippers[member]
		except KeyError:
			self.tippers[member]=0

		tips=self.tippers[member]
		tips += tokens
		self.tippers[member]=tips
		buf="%s has tipped %s %s tokens" % (member, self.camgirl, tokens)
                print buf
                return

	def update_user_info(self, m):	
		u_info = self.do_process_json_message(m)
		self.Name = u_info['nm']
		s_id      = u_info['sid']
		self.g_sid[self.Name]=[self.ws_main ,s_id]
		self.user_level = u_info['lv'] 
		self.memberuid = u_info['uid']


	def do_process_json_message(self, m):
		m = m.replace('\r', '\\r').replace('\n', '\\n')
		try:
			return json.loads(m[m.find("{"):].decode("utf-8","ignore"), strict=False)
		except:
			print "Json processing ERROR ..", m, m[m.find("{"):]
			e, t, tb = sys.exc_info()
			var = traceback.format_exc()
			print ("------------------------------------------")
			print("exception  : \"%s\"" % (t))
			print ("trace back : ", var)
			print ("------------------------------------------")
			return json.loads("{\"lv\":0}")


	def leave_channel(self, m):
		cmsg_pattern = \
			r"(\d+) (?P<SID>\d+) (\d+) (\d+) (\d+)"

		hdr=re.match (cmsg_pattern , m)
		if bool(hdr):
			fmt="%s has left %s%s's%s room"
			sid=int(hdr.group('SID'))
			for usr, [lvl, s_sid, userid] in sorted(self.members.items(),  reverse=True):
				if s_sid==sid:
					del self.members[usr]
					if lvl == 2:
						self.prem -= 1
						#usr=fg.cyan + usr+"("+userid+")" + attr.reset
					elif lvl == 1:
						self.basics -= 1
						#usr=fg.yellow + usr+"("+userid+")" + attr.reset
					break
		else:
			print "ERROR leave chan", m

	def join_channel(self, m):
		join_ms=self.do_process_json_message(m)
		try:
			usr  = join_ms['nm']
			lvl  = join_ms['lv']
			uid  = str(join_ms['uid'])
			sid  = join_ms['sid']
		except:
			return

		try:
			timestamp=join_ms['u']['creation']
			acct=str(unix_epoch_to_PT(timestamp).strftime("%b %d,%Y"))
		except:
			acct = "N/A"
			pass

		self.members[usr]=[lvl ,sid, uid]
		if lvl == 4:
			if self.mid_camgirl==int(uid):
				if self.camgirl != usr:
					self.camgirl=usr
				self.process_user_info(join_ms, 0, 0)
                elif lvl == 2:
			self.prem += 1
		elif lvl == 1:
			self.basics += 1
		#fmt="%s has joined %s%s's%s room"
		#if self.enable_dbg == 0:
		#	if lvl == 4 or lvl == 5:
		#		usr=fg.magenta + attr.bold + usr+"("+uid+")" + attr.reset
		#	elif lvl == 2:
		#		usr=fg.cyan + usr+"("+uid+")" + attr.reset
		#		self.prem += 1
		#	elif lvl == 1:
		#		usr=fg.yellow + usr+"("+uid+")" + attr.reset
		#		self.basics += 1
		#	buf=fmt % (usr, fg.red, self.camgirl,attr.reset)
		#	self.cli_out(buf)

	def process_session_state_change (self, msg):
		vs = -1
		rank = -1
		sess_state = msg
		cg_uid     = sess_state['uid']
		room_count = 0
		cam_srv = -1
		try:
			m_info     = sess_state['m']
		except KeyError:
			pass

		try:
			vs = sess_state['vs']
		except KeyError:
			pass

		try:
			room_count = m_info['rc']
		except:
			pass

		try:
			rank = m_info['rank']
		except:
			pass

		try:
			u_info  = sess_state['u']
			cam_srv = u_info['camserv']
		except KeyError:
			pass

		cguid = str(cg_uid)
                try:
                    data = online_camgirls[cguid]
                except KeyError:
                    '''
		    mem_entry=db_get(db_camgirls, db_wl, cguid)
		    if mem_entry != None:
			    m_data=[mem_entry[0], 0, vs, rank, 0, "", 0, 0, 0]
		    else:
			    m_data=[cguid, 0, vs, rank, 0, "", 0, 0, 0]
                    online_camgirls[cguid] = m_data
                    '''
                    pass

		try:
			if room_count != 0:
				online_camgirls[cguid][8]=room_count
		except:
			pass
		try:
			if vs != -1:
				online_camgirls[cguid][2]=vs
		except:
			pass
		try:
			if cam_srv != -1:
				online_camgirls[cguid][6] = cam_srv
		except:
			pass
		try:
			if rank != -1:
				try:
					#could be offline
					old_rank = online_camgirls[cguid][3] 
					if old_rank != rank:
						online_camgirls[cguid][3] = rank
						#cli_out(bg.white+fg.blue+"%s's rank %d -> %d%s"
						#	% (online_camgirls[cguid][0], old_rank, rank, attr.reset))
				except:
					#cli_out(bg.white+fg.blue+"%s's rank %d%s"
					#	% (online_camgirls[cguid][0], rank, attr.reset))
					pass
		except:
			pass

		if cg_uid == self.mid_camgirl:
			if room_count != 0:
				self.room_count = room_count
			if cam_srv != -1 and cam_srv != self.cam_srv:
				self.cam_srv = cam_srv
			if rank != -1 and rank != self.rank:
				cli_out(fg.green+"%s's rank change %d -> %d%s"
					% (self.camgirl, self.rank, rank, attr.reset))
				self.rank=rank 
			if vs != -1:
				self.show_camgirl_video_state (vs, 0)

	def process_online_camgirl_session_state(self, msg, display, camgirl_id, vs):
		global online_camgirls

		msg = self.do_process_json_message(msg)
		try:
			sid=msg['sid']
		except:
			return

		try:
			usr = msg['nm']
		except KeyError:
			self.process_session_state_change(msg)
			return

		level  = msg['lv']
		camgirl_id = str(msg['uid'])
		camgirlinfo=msg['m']
		topic  = camgirlinfo['topic']
		flags  = camgirlinfo['flags']
		missmfc= camgirlinfo['missmfc']
		vs     = msg['vs']
		continent=camgirlinfo['continent']
		try:
			cs=float(camgirlinfo['camscore'])
		except KeyError:
			cs=0

		try:
			rc=camgirlinfo['rc']
		except KeyError:
			rc=0

		try:
			hide_camscore=camgirlinfo['hidecs']
			if hide_camscore  == True:
				hide_camscore="(hide CS)"
		except KeyError:
			hide_camscore=""

		u_info=msg['u']
		age="N/A"
		Ethnic="N/A"
		country="N/A"

		try:
			timestamp=u_info['creation']
			acct=str(unix_epoch_to_PT(timestamp).strftime("%b %d,%Y"))
		except:
			acct="N/A"
			pass
		try:
			Camserv = u_info['camserv']
			if Camserv >= 500:
				Camserv = Camserv - 500
		except KeyError:
			Camserv=0

		new_camgirl=camgirlinfo['new_model']
		rank = camgirlinfo['rank']
		truepvt = ((flags & 8) == 8)
		chan_id=100000000+int(camgirl_id)

		m_data=[usr, new_camgirl, vs, rank, cs, continent, Camserv, 0, rc]

		online_camgirls[camgirl_id]=m_data

		if self.mid_camgirl == int(camgirl_id):
			self.rank=rank
			self.cs=cs
			self.new_camgirl=new_camgirl
			self.cam_srv = Camserv
			self.show_camgirl_video_state (vs, truepvt)
                        if vs == 127:
                            end_session(self.mid_camgirl)
			return

		return

	def show_camgirl_video_state (self, st, tp):
		try:
			if self.cam_srv == 0 and st == 0:
				self.state = "CAM OFF"
				self.cam_state = 90
				return
			old_vs = self.cam_state
			if st != self.cam_state:
				self.cam_state = st
			if tp == 1:
				state = "TRUEPVT"
			else:
				state=video_state[st]
			if state != self.state:
				if st == 0 or st == 12 or st == 13:
					self.cli_out(fg.red+attr.bold+"%s is in %s%s" 
						% (self.camgirl, state, attr.reset))
				elif st == 90:
					self.cli_out(fg.red+attr.bold+"%s's %s%s" 
						% (self.camgirl, state, attr.reset))
				elif st == 127:
					self.cli_out(fg.red+attr.bold+"%s went %s%s" 
						% (self.camgirl, state, attr.reset))
				elif st == 2:
					self.cli_out(fg.red+attr.bold+"%s is %s%s" 
						% (self.camgirl, state, attr.reset))
			self.state=state
		except KeyError:
			pass

	def process_user_info(self, msg, response_code, send_cmd):
		try:
			sid=msg['sid']
			level  = msg['lv']
		except:
			print "Error : process_user_info", msg
			return
		if sid != 0 and level == 4:
			uid    = str(msg['uid'])
			camgirlinfo=msg['m']
			topic  = camgirlinfo['topic']
			flags  = camgirlinfo['flags']
			missmfc= camgirlinfo['missmfc']
			usr    = msg['nm']
			vs     = msg['vs']
			continent=camgirlinfo['continent']
			try:
				cs=float(camgirlinfo['camscore'])
			except KeyError:
				cs=0
			try:
				hide_camscore=camgirlinfo['hidecs']
				if hide_camscore  == True:
					hide_camscore="(hide CS)"
			except KeyError:
				hide_camscore=""

			u_info=msg['u']
			age="N/A"
			Ethnic="N/A"
			country="N/A"

			try:
				timestamp=u_info['creation']
				acct=str(unix_epoch_to_PT(timestamp).strftime("%b %d,%Y"))
			except:
				acct="N/A"
				pass
			try:
				Camserv = u_info['camserv']
				if Camserv >= 500:
					Camserv = Camserv - 500
			except KeyError:
				Camserv=0

			new_camgirl=camgirlinfo['new_model']
			rank = camgirlinfo['rank']

			if new_camgirl == 1:
				new_camgirl="*NEW*"
			else:
				new_camgirl=""

			truepvt = ((flags & 8) == 8)

			buf=usr+new_camgirl+" ("+acct+" "+continent+") =>"
			if rank != 0:
				buf += " Rank: "+str(rank)
			if cs != 0:
				buf+=" CS: "+str(cs)
			if send_cmd == 1:
				buf+=" Topic: "+topic
			try:
				if truepvt == 1:
					buf+=" (TRUEPVT)"
				else:
					buf+=" ("+video_state[vs]+")"
			except KeyError:
				pass
			if self.mid_camgirl == int(uid):
				self.rank=rank
				self.cs=cs
				self.new_camgirl=new_camgirl
				old_vs = self.cam_state
				self.cam_srv = Camserv
				try:
					if truepvt == 1:
						self.state = "TRUEPVT"
					else:
						self.state=video_state[vs]
				except KeyError:
					self.state="Unknown"
				if old_vs != vs:
					print buf
				self.show_camgirl_video_state (vs, truepvt)

                        '''
			mem_entry=db_get(db_camgirls, db_wl, uid)
			if mem_entry==None:
									  # cur, lest, best
				u_data=[usr, uid, 0, missmfc, age, acct, country, continent, cs, cs, cs]
				db_add(db_camgirls, db_wl, uid, u_data) 
			else:
				mem_entry[5]=acct
				if not usr in mem_entry:
					db_append (db_camgirls, db_wl, uid, usr)
				if cs > 0:
					update_cam_score_details(usr, mem_entry, cs, uid)
                        '''

	def received_message (self,data):
		self.parse_response(self.ws_main, str(data))

	def parse_response (self, ws, data):
		if self.Incomplete_Buf != "":
			data=self.Incomplete_Buf+data
			self.Incomplete_Buf=""
		while True:
			hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", data)
			if bool(hdr) == 0:
				self.cli_out ("not complete data %s" % self.Incomplete_Buf)
				self.cli_out ("ERROR: parse_response failed %s" % data)
				break
                        camgirl_id = int(hdr.group(2))
			msgtype = hdr.group(1)
                        session_id = hdr.group(3)
                        msg_len = int(msgtype[0:6])
                        try:
                            msgtype = int(msgtype[6:]) 
                        except ValueError:
                            print "error .. ", data
			Message = data[6:6+msg_len]
        		if len(Message) < msg_len:
			    self.Incomplete_Buf=''.join(data)
			    break
			if msgtype == 0 or msgtype == 64 or msgtype == 4 or msgtype == 43 or msgtype == 44:
				data=data[6+msg_len:]
				if len(data) == 0:
					break
				continue
			else:
				Message=urllib.unquote(Message)

			if msgtype == 6:
				self.tip_msg (Message)
			elif msgtype == 51:
				lorj = int(hdr.group(5))
				if lorj == 1:
					self.join_channel(Message)
				if lorj == 2:
					self.leave_channel (Message)
			elif msgtype == 46:
				self.guests_count=int(hdr.group(4))
				self.joined=1
			elif msgtype == 20:
				camgirl_id=hdr.group(5)
				mid=int(camgirl_id)
				vs=int(hdr.group(4))
				if self.mid_camgirl==mid:
					if vs == 127:
						self.cam_state = vs
						self.state = video_state[vs]
						ret_val=end_session(int(camgirl_id))
						try:
							del online_camgirls[camgirl_id]
						except KeyError:
							pass
					else:
						self.process_online_camgirl_session_state(Message, 0, camgirl_id, vs)
				elif mid==0:
					self.session_IO=2
					#time.sleep(1)
					self.Name=None
					self.close_session()
					break
			elif msgtype == 11:
				msg=self.do_process_json_message(Message)
				username=None
				try:
					username = msg['event']['username']
					level    = msg['event']['lv']
				except:
					username=None
					pass
				if username != None:
					if self.last_banned_member != username:
						global cg_bans
						if level > 0:
							buf=username+"("+ self.camgirl+")"
							try:
								cg_bans[self.camgirl.lower().lower()].append(username)
							except KeyError:
								cg_bans[self.camgirl.lower()]=[]
								cg_bans[self.camgirl.lower()].append(username)

							buf=fg.red+buf+attr.reset
							print(buf)
							self.last_banned_member=username
					elif self.Name == username:
						cli_out(fg.red+"IP is banned :  "+self.camgirl+\
							"'s room .. closing connection: "+ attr.reset)
						try:
							if enable_tor == 1:
								New_tor_id()
								self.exit_session=0
							else:
								self.exit_session=1
							self.session_IO=0
							self.ws_main.send("98 0 0 0 0 -\n\0")
							self.ws_main.close()
						except:
							cli_out(fg.red+"Error in closing connection"+attr.reset)
						pass
			elif msgtype == 10:
                                print "10 ... ", Message
				response_code=int(hdr.group(5))
				r_code = response_code
				camgirl_id=int(hdr.group(2))
				if response_code == 0 or response_code == 4:
					Message=self.do_process_json_message(Message)
					if self.mchanid == 0 and Message['nm'].lower() == self.camgirl.lower():
						camgirl_id=Message['uid']
						r_code = 0
				if camgirl_id != 0 and r_code == 0:
					if self.mchanid == 0:
						self.mid_camgirl=camgirl_id
						self.process_user_info(Message, response_code, 0)
						self.mchanid=100000000+int(camgirl_id)
						self.join_room (ws)
						self.session_IO=1
						client.append(self)
					else:
						self.process_user_info(Message, response_code, 1)
				elif response_code == 10 or response_code == 1:
					Message=Message.split(' ')
					if self.mchanid == 0:
						try:
							cli_out (fg.red + attr.bold + Message[5] + \
								 " is not a valid user" + attr.reset)
						except IndexError:
							cli_out (fg.red + attr.bold + " " + \
								 " is not a valid user" + attr.reset)
						#self.timer_join.cancel()
						self.session_IO=2
						time.sleep(1)
						self.Name=None
						self.close_session()
						break
				else:
					self.process_user_info(Message, response_code, 1)
			elif msgtype == 63:
				self.session_IO=0
				#self.timer_join.cancel()
				self.joined=1
				self.guest_conn += 1
				cli_out(fg.blue+"Joined \"%s's\" chat%s"  % 
					(self.camgirl, attr.reset))
			elif msgtype == 1:
				self.sess_id=int(hdr.group(3))
				self.joined=0
				#180 :dunno
				if self.mchanid==0:
					if self.mid_camgirl == -1:
					        ws.send("10 0 0 20 0 %s\n\0" % self.camgirl)
					else:
						self.mchanid=100000000+self.mid_camgirl
						self.join_room (ws)
						client.append(self)
			elif msgtype == 5:
				self.update_user_info (Message)
			elif msgtype == 14:
                            try:
				Message = self.do_process_json_message(Message)	
                                count = Message['count']
                                data = Message['rdata']
                                i=1
                                while i < len(data):
                                            try:
                                                lvl = data[i][0]
                                                usr = data[i][1]
                                                sid = data[i][2]
                                                uid = data[i][3]
                                		self.members[usr]=[lvl ,sid, uid]
                                                if lvl == 2:
                                                        self.prem += 1
                                                elif lvl == 1:
                                                        self.basics += 1
                                            except:
                                                self.process_user_info(data[i], 0, 0)
                                                pass
                                            i= i + 1
                            except:
                                pass

			data=data[6+msg_len:]
			if len(data) == 0:
				break
		
	def guests_remove(self, count):
		i=0
		for guests, [ws, s_sid] in self.g_sid.items():
			if ws == self.ws_main:
				continue
			ws.send("98 0 0 0 0 -\n\0")
			ws.close()
			i += 1
			if i == count:
				break
	def show_members(self):
		i=0
		member=sorted(self.members.keys(), key=lambda x: self.members[x], reverse=True)
		out_buf=""
		for usr in member:
			try:
				lvl=self.members[usr][0]
				userid=self.members[usr][2]
				if lvl == 4 or lvl == 5:
					usr=fg.magenta + usr
				elif lvl == 2:
					usr=fg.cyan + usr
				elif lvl == 1:
					usr=fg.yellow + usr
				out_buf+="%-14s%s" %(usr, attr.reset)
				i += 1
				if i % 6 == 0:
					out_buf+="\n"
				else:
					out_buf+="\t"
			except KeyError:
				pass
		cli_out(out_buf)
		mem_coun=i
		cli_out ("(%d prem/basics) (%d guests)" % (mem_coun, self.guests_count))
		cli_out("%d People\n" % self.room_count);

	def join_room(self, ws):
		ws.send("51 0 0 %d 9 -\n\0" % (self.mchanid)); 

	def show_tip_details(self):
		if self.total_tips == 0:
			return
		cli_out("--------------Members Cumulative Tips --------------------")
		mem_tippers=sorted(self.tippers, key=lambda x: self.tippers[x], reverse=True)
		for mem_key in mem_tippers:
			cli_out ("%-24s : %8d" % (mem_key, self.tippers[mem_key]))
		cli_out("----------------------------------------------------------")

	def connect_2_mfc_chat_server_chat(self, host):
		#cli_out("Connecting to Chat Server... %d" % (self.guest_conn))
            	client = guest_client(host, userdata=[self])
		client.guest_name=None
		client.websockmgr=self
		try:
			client.connect ()
		except:
			#e, t, tb = sys.exc_info()
			#print("Could not connect guest session to \"%s\"" % (t))
			print("Could not able to connect to chat server")
			del client

	def add_guest (self, count):
		global gbot_ka_thr
		if self.gbot_ka_thr == None:
			self.gbot=WebSocketManager(name="Guest Bot")
			self.gbot.start()
			self.gbot_ka=1
			self.gbot_ka_thr=threading.Thread(target=self.run_guest_cli_keep_alive)
			self.gbot_ka_thr.setDaemon(True)
			self.gbot_ka_thr.start()

		i=0
		while True:
			self.connect_2_mfc_chat_server_chat(get_chat_host())
			i += 1
			if self.guest_conn % 20 == 0:
				New_tor_id()
				time.sleep(1)
			if i >= count:
				time.sleep(2)
				print "Total Guests count added",  self.guest_conn
				return
		time.sleep(2)
		print "Total Guests count added", self.guest_conn
		return

	def session_handle_command(self, line, websk, sid):
		help_string="Help : \n/g <count> - Add guest(s)\n" \
			     "/r <count> - Remove guest(s)\n/s <account_name> - online status of a member/camgirl\n"\
			     "/m - Members in the room \n" \
			     "/p - For PM \n" \
			    "/i - To ignore a user\n/u - To stop ignoring user\n/t - tokens info\n" \
			    "/ec - Enable Chat Commands\n/dc - Disable Chat Commands\n" \
			    "/es - Enable Spam\n/ds - Disable Spam" \
			    "/ea - Auto reply to user \n/da - Disable auto reply"
		if line[0] == '/':
			if len(line) >= 2:
				if line[1] == 't':
					cli_out("Tokens          : %-05d" % self.total_tips)
					self.show_tip_details ()
					print "Total Guests count ", self.guest_conn, self.gcount
				elif line[1] == 'g':
					line=line.split()
					try:
						count=line[1]
						count=s2i(count)
						self.add_guest (count)
					except IndexError:
						self.add_guest (1)
				elif line[1] == 'r':
					line=line.split()
					try:
						count=line[1]
						count=s2i(count)
						self.guests_remove (count)
					except IndexError:
						self.guests_remove (1)
				elif line[1] == 'm':
					self.show_members()
				elif line[1] == 'h':
					cli_out(help_string)
				elif line[1]=='s':
					Name=line[3:]
					if len(Name) == 0:
						cli_out(fg.red+ "Not a valid username"+attr.reset)
						return
					self.ws_main.send("10 0 0 20 0 %s\n\0" % Name)
					time.sleep(2)
				elif line[1]=='S':
					newcamgirl=""
					if self.new_camgirl == 1:
						newcamgirl="*NEW*"
					cli_out(fg.green+"     %-10s %s (%s)%s" %
						(self.camgirl, newcamgirl, self.state, attr.reset))
					if self.rank != 0:
						cli_out("     Rank            : %-05d" % self.rank)
					if self.total_tips != 0:
						cli_out("     Tokens          : %-05d" % self.total_tips)
					cli_out("     CS              : %-05s" % str(self.cs))
					cli_out("     Prem|Basic|Guest: %d|%d|%d (%d)" 
						% (self.prem, self.basics, self.guests_count, self.room_count))
					now = int(time.time())
					cli_out("     Active for      : %-05s(hh:mm:ss) (%s)" % (
						str(datetime.timedelta(seconds=now-self.start)), self.connected_on))
				elif line[1]=='q':
					self.session_IO=0
					return
				else:
					cli_out(help_string)
		else:
			if self.user_level == 0:
				line=line
			else:
				line=Process_input_message(line, self.user_level)
			try:
				websk.send("50 %d %d 0 0 %s\n\0" % (sid, self.mchanid, line))
			except:
				pass
			#time.sleep(1)

	def session_input(self):
		while self.session_IO:
			try:
                                conn=1
                                if self.guest_conn != 0:
                                    conn=self.guest_conn
				rand=random.randint(1, conn)
			except ValueError:
                                print "errro"
				if self.guest_conn == 0:
					return
			sid=self.sess_id
			guest=self.Name
			websk=self.ws_main
			line = read_input(fg.green + str(guest).strip('"')+">"+attr.reset)
			if len(line) > 1:
				self.session_handle_command(line, websk, sid)
