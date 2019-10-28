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

#FCS.FCVIDEO_TX_IDLE = 0; FCS.FCVIDEO_TX_RESET = 1; FCS.FCVIDEO_TX_AWAY = 2; FCS.FCVIDEO_TX_CONFIRMING = 11; FCS.FCVIDEO_TX_PVT = 12; FCS.FCVIDEO_TX_GRP = 13; FCS.FCVIDEO_TX_CLUB = 14; FCS.FCVIDEO_TX_KILLMODEL = 15; FCS.FCVIDEO_C2C_ON = 20; FCS.FCVIDEO_C2C_OFF = 21; FCS.FCVIDEO_RX_IDLE = 90; FCS.FCVIDEO_RX_PVT = 91; FCS.FCVIDEO_RX_VOY = 92; FCS.FCVIDEO_RX_GRP = 93; FCS.FCVIDEO_RX_CLUB = 94; FCS.FCVIDEO_NULL = 126; FCS.FCVIDEO_OFFLINE = 

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
	socket.socket=old_socket
	try:
	        TorCtl.Connection.send_signal(Tor_conn, "NEWNYM")
	except:
		cli_out(fg.red+"Control connection closed. Reconnect ...")
		time.sleep(15)
		init_tor_connect('localhost', 9052)
		time.sleep(1)
	        TorCtl.Connection.send_signal(Tor_conn, "NEWNYM")
	socket.socket = socks.socksocket

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
