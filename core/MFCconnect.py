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
from websocket import create_connection
from core.timezone import *
from core.cmn import *
from core.database import Database
from core.mfccuck import connect_xchat_server

online_camgirls={}
camgirlslist=[]
modelsonline=0
membersonline=0
knowncamgirls={}
online_models_update_thread_interval=90
api_models_update_thread_interval=95
api_record_stats_thread_interval=1200


def read_camgirls_list():
	global camgirlslist
        camgirlslist=[]
        try:
            r = APIep.get({},'models?limitInfo=1&watch=1')
            file1 = json.loads(r)
            # file1 = open('models.txt', 'r')
	except:
		print "No file models.txt"
		return

        # file1.seek(0, os.SEEK_SET)
        for camgirl in file1:
                #camgirl=camgirl.strip('\n')
                #camgirl=camgirl.strip().lower()
                camgirl = camgirl['name']
               
                if camgirl not in camgirlslist:
                    #print ("Adding \"%s\' to monitor list\n" %(camgirl))
                    camgirlslist.append(camgirl.lower())
        # file1.close()

def connect_camgirl_room(camgirl, uid, vs, fl):
        global total_connections
	retry = 0
	is_dup=0
	for session in client:
		if session.camgirl.lower() == camgirl.lower():
			#cli_out(fg.red+"Active session for camgirl '%s' is running%s" 
			#		%(camgirl, attr.reset))
			return
	while retry < 2:
		session=connect_xchat_server(camgirl, uid, vs, fl)
		if session==None:
			time.sleep(0.5)
			New_tor_id()
			time.sleep(1)
			retry += 1
		else:
			return session
	return None

def online_models_update_thread():
    global online_models_update_thread_interval
    while True:
        read_camgirls_list()
        try:
            MFCCtl()
        except:
            pass
        time.sleep(online_models_update_thread_interval)

def MFCCtl():
        global camgirlslist
        global membersonline
        global modelsonline
        host = "wss://"+random.choice(xchat)+".myfreecams.com:443/fcsl"
        ws = create_connection(host)
        ws.send("fcsws_20180422\n\0")
        ws.send("1 0 0 20071025 0 1/guest:guest\n\0")
        rembuf=""
        quitting = 0
        i=0
        while quitting == 0:
                sock_buf =  ws.recv()
                sock_buf=rembuf+sock_buf
                rembuf=""
                while True:
                        i=i+1
                        #print sock_buf
                        hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", sock_buf)
                        if bool(hdr) == 0:
                                break

                        fc = hdr.group(1)

                        mlen   = int(fc[0:6])
                        fc_type = int(fc[6:])

                        msg=sock_buf[6:6+mlen]

                        if len(msg) < mlen:
                                rembuf=''.join(sock_buf)
                                break

                        '''
                        print "---------------------------" + str(i) + "---------------"
                        print msg
                        print "--------------------------------------------------------"
                        '''
                        if fc_type == 81:
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
                                            ct=str(unix_epoch_to_PT(m[11]).strftime("%b %d,%Y"))
                                            #u'camscore', u'continent', u'flags', u'rank', u'rc', 
                                            cs=m[18]
                                            cntient=m[19]
                                            fl=m[20]
                                            rank=m[21]
                                            rc=m[22]
                                            total+=rc
                                            online_camgirls[uid]=[nm , vs, ct, cs, fl, rank, rc, cntient]
                                            if nm.lower() in camgirlslist:
                                                connect_camgirl_room(nm, uid, vs, fl)
                                            i= i + 1
                                print "Total Models = ", i
                                print "Total viewers = ", total
                                membersonline=total
                                modelsonline=i
                                quitting=1

                        sock_buf=sock_buf[6+mlen:]

                        if len(sock_buf) == 0:
                                break
        ws.close()

def api_record_stats_thread():
    global api_record_stats_thread_interval
    while True:
        try:     
            api_record_stats()
        except:
            pass
        time.sleep(api_record_stats_thread_interval)

def api_record_stats():
    global modelsonline
    global membersonline
    try:
        if modelsonline > 0 or membersonline > 0:
            stat = {
                "siteId": 1, 
                "models": modelsonline,
                "members": membersonline
            }
            APIep.post(stat, 'stats')
    except Exception as e: print(e)
    pass

def api_models_update_thread():
    global api_models_update_thread_interval
    while True:
        try:     
            api_models_update()
        except:
            pass
        time.sleep(api_models_update_thread_interval) 

def api_models_update():
    global knowncamgirls
    modelsupdated = 0
    modelsinserted = 0
    modelsskipped = 0
    
    print 'Starting API model update...'
    if len(knowncamgirls) == 0:
        print 'Getting all known models from API...'
        r = APIep.get({},'models?limitInfo=1')
        knowncamgirlsjson = json.loads(r)
        # convert response to indexed dict
        for girl in knowncamgirlsjson:
            knowncamgirls[girl['id']] = [girl['name'], girl['score']] # {5531429: [u'sweetchanel4u', 107]

    for girl in online_camgirls:
        # print girl '44212343'
        # print online_camgirls[girl] [u'Liceth26', 0, 'Nov 06,2018', 478.4, 539680, 0, 2, 'US']
        id = girl
        name = online_camgirls[girl][0]
        score = online_camgirls[girl][3]
        rank = online_camgirls[girl][5]
        createdAt = online_camgirls[girl][2]
        continent = online_camgirls[girl][7]
        data = {
            "id": id,
            "name": name,
            "siteId": "1",
            "continent": continent,
            "score": score,
            "modelRank:": rank,
            "modelCreatedAt": createdAt,
        }
        try: 
            knowncamgirls[id]
        except:
            # Insert new model
            APIep.post(data, 'models')
            knowncamgirls[girl]=[name, score]
            modelsinserted+=1
            continue
        # check if the lastest info matches what we have
        if int(round(score)) == knowncamgirls[girl][1]:
            modelsskipped+=1
        else:
            # print 'update this one'
            APIep.patch(data, 'models')
            knowncamgirls[girl]=[name, (round(score))]
            modelsupdated+=1
            
    print 'Inserted ', modelsinserted, ' | ', 'Updated ', modelsupdated, ' | ', 'Skipped ', modelsskipped

def start_mgr():
    MFCkathread=threading.Thread(target=online_models_update_thread)
    MFCkathread.setDaemon(True)
    MFCkathread.start()
    stats=threading.Thread(target=api_record_stats_thread)
    stats.setDaemon(True)
    stats.start()
    models=threading.Thread(target=api_models_update_thread)
    models.setDaemon(True)
    models.start()