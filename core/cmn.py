import socket
import datetime
import random
import pytz
import json
import socks as socks
import time

client=[]
enable_tor=0
old_socket=socket.socket
def cli_out (f_arg, *argv):
	msg=f_arg
	for arg in argv:
		msg=msg+arg
	msg=msg+attr.reset
	print (msg)
account={}
account[0]=""
account[1]="B"
account[2]="P"
account[4]="M"
account[5]="A"

rcode={}
rcode[2]="NOTICE"
rcode[3]="SUSPEND"
rcode[4]="SHUTOFF"
rcode[5]="WARNING"



class attr:
	reset='\033[0m'
	bold='\033[01m'
	dim='\033[02m'
	normal='\033[22m'
class fg:
	black='\033[30m'
	red='\033[31m'
	green='\033[32m'
	yellow='\033[33m'
	blue='\033[34m'
	magenta='\033[35m'
	cyan='\033[36m'
	white='\033[37m'
class bg:
	black='\033[40m'
	red='\033[41m'
	green='\033[42m'
	yellow='\033[43m'
	blue='\033[44m'
	magenta='\033[45m'
	cyan='\033[46m'
	white='\033[47m'


xchat=[ "xchat108","xchat61","xchat94","xchat109","xchat22","xchat47",
        "xchat48","xchat49","xchat95","xchat20","xchat111","xchat112",
        "xchat113","xchat114","xchat115","xchat116","xchat118","xchat119",
        "xchat42","xchat43","xchat44","xchat45","xchat46","xchat120",
        "xchat121","xchat122","xchat123","xchat124","xchat125","xchat126",
        "xchat67","xchat66","xchat62","xchat63","xchat64","xchat65",
        "xchat23","xchat24","xchat69","xchat70","xchat71","xchat72",
        "xchat73","xchat74","xchat75","xchat76","xchat77","xchat60",
        "xchat80","xchat30","xchat31","xchat32","xchat33","xchat34",
        "xchat35","xchat36","xchat90","xchat91","xchat92","xchat93",
        "xchat81","xchat83","xchat79","xchat68","xchat78","xchat84",
        "xchat85","xchat86","xchat87","xchat88","xchat89","xchat96",
        "xchat97","xchat98","xchat99","xchat100","xchat101","xchat102",
        "xchat103","xchat104","xchat105","xchat106","xchat127"]

#FCVIDEO_TX_IDLE = 0; FCVIDEO_TX_RESET = 1; FCVIDEO_TX_AWAY = 2; FCVIDEO_TX_CONFIRMING = 11; FCVIDEO_TX_PVT = 12; FCVIDEO_TX_GRP = 13; FCVIDEO_TX_CLUB = 14; FCVIDEO_TX_KILLMODEL = 15; FCVIDEO_C2C_ON = 20; FCVIDEO_C2C_OFF = 21; FCVIDEO_RX_IDLE = 90; FCVIDEO_RX_PVT = 91; FCVIDEO_RX_VOY = 92; FCVIDEO_RX_GRP = 93; FCVIDEO_RX_CLUB = 94; FCVIDEO_NULL = 126; FCVIDEO_OFFLINE = 
 #FCS.FCTYPE_ADDIGNORE = 7; FCS.FCTYPE_PRIVACY = 8; FCS.FCTYPE_ADDFRIENDREQ = 9; FCS.FCTYPE_USERNAMELOOKUP = 10; FCS.FCTYPE_ZBAN = 11; FCS.FCTYPE_BROADCASTNEWS = 12; FCS.FCTYPE_ANNOUNCE = 13; FCS.FCTYPE_MANAGELIST = 14; FCS.FCTYPE_INBOX = 15; FCS.FCTYPE_GWCONNECT = 16; FCS.FCTYPE_RELOADSETTINGS = 17; FCS.FCTYPE_HIDEUSERS = 18; FCS.FCTYPE_RULEVIOLATION = 19; FCS.FCTYPE_SESSIONSTATE = 20; FCS.FCTYPE_REQUESTPVT = 21; FCS.FCTYPE_ACCEPTPVT = 22; FCS.FCTYPE_REJECTPVT = 23; FCS.FCTYPE_ENDSESSION = 24; FCS.FCTYPE_TXPROFILE = 25; FCS.FCTYPE_STARTVOYEUR = 26; FCS.FCTYPE_SERVERREFRESH = 27; FCS.FCTYPE_SETTING = 28; FCS.FCTYPE_BWSTATS = 29; FCS.FCTYPE_TKX = 30; FCS.FCTYPE_SETTEXTOPT = 31; FCS.FCTYPE_SERVERCONFIG = 32; FCS.FCTYPE_MODELGROUP = 33; FCS.FCTYPE_REQUESTGRP = 34; FCS.FCTYPE_STATUSGRP = 35; FCS.FCTYPE_GROUPCHAT = 36; FCS.FCTYPE_CLOSEGRP = 37; FCS.FCTYPE_UCR = 38; FCS.FCTYPE_MYUCR = 39; FCS.FCTYPE_SLAVECON = 40; FCS.FCTYPE_SLAVECMD = 41; FCS.FCTYPE_SLAVEFRIEND = 42; FCS.FCTYPE_SLAVEVSHARE = 43; FCS.FCTYPE_ROOMDATA = 44; FCS.FCTYPE_NEWSITEM = 45; FCS.FCTYPE_GUESTCOUNT = 46; FCS.FCTYPE_PRELOGINQ = 47; FCS.FCTYPE_MODELGROUPSZ = 48; FCS.FCTYPE_ROOMHELPER = 49; FCS.FCTYPE_CMESG = 50; FCS.FCTYPE_JOINCHAN = 51; FCS.FCTYPE_CREATECHAN = 52; FCS.FCTYPE_INVITECHAN = 53; FCS.FCTYPE_QUIETCHAN = 55; FCS.FCTYPE_BANCHAN = 56; FCS.FCTYPE_PREVIEWCHAN = 57;
# FCS.FCTYPE_SHUTDOWN = 58; FCS.FCTYPE_LISTBANS = 59; FCS.FCTYPE_UNBAN = 60; FCS.FCTYPE_SETWELCOME = 61; FCS.FCTYPE_CHANOP = 62; FCS.FCTYPE_LISTCHAN = 63; FCS.FCTYPE_TAGS = 64; FCS.FCTYPE_SETPCODE = 65; FCS.FCTYPE_SETMINTIP = 66; FCS.FCTYPE_UEOPT = 67; FCS.FCTYPE_HDVIDEO = 68; FCS.FCTYPE_METRICS = 69; FCS.FCTYPE_OFFERCAM = 70; FCS.FCTYPE_REQUESTCAM = 71; FCS.FCTYPE_MYWEBCAM = 72; FCS.FCTYPE_MYCAMSTATE = 73; FCS.FCTYPE_PMHISTORY = 74; FCS.FCTYPE_CHATFLASH = 75; FCS.FCTYPE_TRUEPVT = 76; FCS.FCTYPE_BOOKMARKS = 77; FCS.FCTYPE_EVENT = 78; FCS.FCTYPE_STATEDUMP = 79; FCS.FCTYPE_RECOMMEND = 80; FCS.FCTYPE_EXTDATA = 81; FCS.FCTYPE_NOTIFY = 84; FCS.FCTYPE_PUBLISH = 85; FCS.FCTYPE_XREQUEST = 86; FCS.FCTYPE_XRESPONSE = 87; FCS.FCTYPE_EDGECON = 88; FCS.FCTYPE_XMESG = 89; FCS.FCTYPE_CLUBSHOW = 90; FCS.FCTYPE_CLUBCMD = 91; FCS.FCTYPE_ZGWINVALID = 95; FCS.FCTYPE_CONNECTING = 96; FCS.FCTYPE_CONNECTED = 97; FCS.FCTYPE_DISCONNECTED = 98; FCS.FCTYPE_LOGOUT = 99; FCS.FCRESPONSE_SUCCESS = 0; FCS.FCRESPONSE_ERROR = 1; FCS.FCRESPONSE_NOTICE = 2; FCS.FCRESPONSE_SUSPEND = 3; FCS.FCRESPONSE_SHUTOFF = 4; FCS.FCRESPONSE_WARNING = 5; FCS.FCRESPONSE_QUEUED = 6; FCS.FCRESPONSE_NO_RESULTS = 7; FCS.FCRESPONSE_CACHED = 8; FCS.FCRESPONSE_JSON = 9; FCS.FCRESPONSE_INVALIDUSER = 10; FCS.FCRESPONSE_NOACCESS = 11; FCS.FCRESPONSE_NOSPACE = 12;
 

FCOPT_TRUEPVT=8
FCOPT_TOKENAPPROX=64
FCOPT_TOKENHIDE=128
FCOPT_GUESTMUTE=4096
FCOPT_BASICMUTE=8192

video_state={}
video_state[0]="PUBLIC"
video_state[2]="AWAY"
video_state[12]="PVT"
video_state[13]="GROUP"
video_state[14]="CLUB"
video_state[90]="CAM OFF"
video_state[127]="OFFLINE"
video_state[128]="TRUEPVT"

xchat_index=0
total_connec=0

def read_input(prompt):
	try:
		return raw_input (prompt)
	except EOFError:
		return ""


def get_chat_host():
        global total_connec
	global xchat_index
        xchat_index=random.randint(0, len(xchat))
	try:
	        host ="wss://"+str(xchat[xchat_index])+".myfreecams.com:443/fcsl"
	except:
		xchat_index = 0
	        host ="wss://"+str(xchat[xchat_index])+".myfreecams.com:443/fcsl"
	xchat_index += 1
	total_connec += 1
	if total_connec % 20 == 0:
		New_tor_id()
		time.sleep(2)
	if xchat_index >= len(xchat):
		xchat_index=0
	return host

Year_Month=["January", "February", "March", 
            "April", "May", "June", "July", 
            "August", "September", "October", 
            "November", "December"]

def get_tor_new_identity():
        return

def enabletor():
	socks.set_default_proxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9099)
	socket.socket = socks.socksocket
	print ("Tor settings enabled")

def disable_tor():
	socket.socket = old_socket
	enable_tor=0

def New_tor_id():
	get_tor_new_identity()


def fc_decode_json(m):
        try:
                m = m.replace('\r', '\\r').replace('\n', '\\n')
                return json.loads(m[m.find("{"):].decode("utf-8","ignore"))
        except:
                return json.loads("{\"lv\":0}")

def unix_epoch_to_PT(ux_epoch):
        utc_date = datetime.datetime.fromtimestamp(ux_epoch, tz=pytz.utc)
        date_PT = utc_date.astimezone(pytz.timezone('US/Pacific'))
        return date_PT
