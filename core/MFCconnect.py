#!/usr/bin/python
import os
import time
import urllib
import sys
import pytz
import re
import threading
import math
import time
import datetime
import socket
import json
import requests
import random
from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
from core.timezone import *
from core.cmn import *
from core.database import Database
from core.mfccuck import connect_xchat_server

MFCsockmgr = WebSocketManager()

Mdb=None
online_camgirls={}
def main_keep_alive(web_sock):
        print "Starting Keep alive for MFCsockmgr\n"
	while web_sock.is_running == 1:
		s_time=(math.floor(10 * random.random()) + 10)
                #print s_time
                time.sleep(s_time);
		try:
       			for ws in web_sock.websockets.itervalues():
				if not ws.terminated:
					ws.send("0 0 0 0 0 -\n\0")
		except:
			pass


def process_online_camgirl_session_state(msg, display, camgirl_id, vs):
        global online_camgirls

        msg = fc_decode_json(msg)
        try:
                sid=msg['sid']
        except:
                return

        try:
                usr = msg['nm']
        except KeyError:
                #process_session_state_change(msg)
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
                rc=float(camgirlinfo['rc'])
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

        new_camgirl=camgirlinfo['new_model']
        rank = camgirlinfo['rank']
        truepvt = ((flags & 8) == 8)
        chan_id=100000000+int(camgirl_id)

        m_data=[usr, new_camgirl, vs, rank, cs, continent, 0, rc, acct]
        #print usr, camgirl_id, rank, cs, continent, 0, rc, acct

        data = {
                "name": usr,
                "modelId": camgirl_id,
                "siteId": "1",
                "country": "",
                "continent": continent,
                "ethnic": "",
                "score": cs,
                "rank:": rank,
                "modelCreatedAt": acct
        }
        
        online_camgirls[camgirl_id]=m_data
        return

def connect_camgirl_room(camgirl, uid):
	retry = 0
	is_dup=0
	for session in client:
		if session.camgirl.lower() == camgirl.lower():
			if camgirl.lower() not in guest_lounge_camgirl:
				cli_out(fg.red+"Active session for camgirl '%s' is running%s" 
						%(camgirl, attr.reset))
			is_dup=1
			break
	if is_dup == 1:
		return
	while retry < 2:
		session=connect_xchat_server(camgirl, uid)
		if session==None:
			time.sleep(0.5)
			New_tor_id()
			time.sleep(1)
			retry += 1
		else:
			return session
	return None

class MFCCtl(WebSocketBaseClient):
	def handshake_ok(self): 
            self.rembuf=""
	    MFCsockmgr.add(self)
	    self.ws=MFCsockmgr.websockets[self.sock.fileno()]
            self.ws.send("fcsws_20180422\n\0")
            self.ws.send("1 0 0 20071025 0 1/guest:guest\n\0")
	def connection_closed(self):
            print "connection closed"
	def received_message (self,data):
		self.parse_response(self.ws, str(data))
	def parse_response (self, ws, data):
	    if self.rembuf != "":
		data=self.rembuf+data
		self.rembuf=""
            while True:
                    hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", data)
                    if bool(hdr) == 0:
                            break

                    fc = hdr.group(1)

                    mlen   = int(fc[0:6])
                    fc_type = int(fc[6:])

                    msg=data[6:6+mlen]

                    if len(msg) < mlen:
                            rembuf=''.join(data)
                            break

                    '''
                    print "---------------------------" + str(i) + "---------------"
                    print msg
                    print "--------------------------------------------------------"
                    '''
                    if fc_type == 20:
                            msg=urllib.unquote(msg)
                            camgirl_id=hdr.group(5)
                            mid=int(camgirl_id)
                            vs=int(hdr.group(4))
                            process_online_camgirl_session_state(msg, 0, camgirl_id, vs)
                    elif fc_type == 81:
                        msg=urllib.unquote(msg)
                        m=fc_decode_json(msg)
                        ty=m['type']
                        opts=m['opts']
                        respkey=m['respkey']
                        arg1=m['msg']['arg1']
                        arg2=m['msg']['arg2']
                        serv=m['serv']
                        if ty == 14 and arg1 != 0:
                            req=""
                            if respkey != 0:
                                req+="respkey="+str(respkey)+"&"
                            if ty != 0:
                                req+="type="+str(ty)+"&"
                            if opts != 0:
                                req+="opts="+str(opts)+"&"
                            if serv != 0:
                                req+="serv="+str(serv)+"&"
                            if arg1 != 0:
                                req+="arg1="+str(arg1)+"&"
                            if arg2 != 0:
                                req+="arg2="+str(arg2)+"&"
                            req+="owner=0&nc="+str(int(random.random()))
                            r=requests.get("https://www.myfreecams.com/php/FcwExtResp.php?"+req)
                            '''
                            [u'nm', u'sid', u'uid', u'vs', u'pid', u'lv', {u'u': [u'camserv', u'phase', u'chat_color', u'chat_font', u'chat_opt', u'creation', u'avatar', u'profile', u'photos', u'blurb']}, {u'm': [u'new_model', u'missmfc', u'camscore', u'continent', u'flags', u'rank', u'rc', u'topic', u'hidecs']}, {u'x': [u'share.albums', u'share.follows', u'share.clubs', u'share.tm_album', u'share.collections', u'share.stores', u'share.goals', u'share.polls', u'share.things', u'share.recent_album_tm', u'share.recent_club_tm', u'share.recent_collection_tm', u'share.recent_goal_tm', u'share.recent_item_tm', u'share.recent_poll_tm', u'share.recent_story_tm', u'share.recent_album_thumb', u'share.recent_club_thumb', u'share.recent_collection_thumb', u'share.recent_goal_thumb', u'share.recent_item_thumb', u'share.recent_poll_thumb', u'share.recent_story_thumb', u'share.recent_album_title', u'share.recent_club_title', u'share.recent_collection_title', u'share.recent_goal_title', u'share.recent_item_title', u'share.recent_poll_title', u'share.recent_story_title', u'share.recent_album_slug', u'share.recent_collection_slug', u'share.tipmenus', u'social.uname', u'social.posts', u'social.tm_post']}]
                            '''
                            a=json.loads(r.text)
                            info = a['rdata']
                            i=1
                            total = 0
                            while i < len(info):
                                        m=info[i]
                                        nm=m[0]
                                        sid=m[1]
                                        uid=m[2]
                                        vs=m[3]
                                        csr=m[6]
                                        ct=str(unix_epoch_to_PT(m[11]).strftime("%b %d,%Y"))
                                        #u'camscore', u'continent', u'flags', u'rank', u'rc', 
                                        cs=m[18]
                                        cntient=m[19]
                                        fl=m[20]
                                        rank=m[21]
                                        rc=m[22]
                                        total+=rc
                                        '''
                                        Mdb.insertmodel(nm, uid, ct, 0, cs)
                                        Mdb.updatecs(uid, cs)
                                        Mdb.updaterc(uid, int(rc))
                                        '''
                                        if int(cs) > 10000:
                                            online_camgirls[uid]=[nm , vs, ct, cs, fl, rank, rc]
                                            connect_camgirl_room(nm, uid)
                                        i= i + 1
                            print "Total viewers = ", total
                            print online_camgirls
                    data=data[6+mlen:]

                    if len(data) == 0:
                            break
def start_mgr():
    MFCsockmgr.start()
    MFCsockmgr.is_running=1
    MFCkathread=threading.Thread(target=main_keep_alive, args=[MFCsockmgr])
    MFCkathread.setDaemon(True)
    MFCkathread.start()
    host=get_chat_host()
    print host
    MFCsess=MFCCtl(host)
    MFCsess.connect()
