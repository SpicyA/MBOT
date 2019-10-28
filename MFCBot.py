#!/usr/bin/python
# coding: utf-8
# encoding=utf8  
import os
import signal
import time
import traceback
import urllib
import sys
import socket
import socks
#socks.set_default_proxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9099)
#socket.socket = socks.socksocket
from core.mfccuck import main_session, start_cuckmgr, connect_xchat_server
from core.MFCconnect import start_mgr
from core.timezone import *
from core.cmn import *
import json
from websocket import create_connection
import datetime
from ws4py import configure_logger
import logging

reload(sys)  
sys.setdefaultencoding('utf8')

startup_time = int(time.time())

def session_info_header():
	cli_out(fg.red+"** Active Session(s) **"+attr.reset)
	cli_out("%-05s     %-10s" % ("Id", "Name"))
	cli_out(fg.red+"***********************"+attr.reset)


def process_global_commands(line):
	global client
	help_string="Help : \n/c - Connect to Model's Room (new session)\n/j - Join Model's active session \n" \
                     "/l - List active sessions\n/t - Close an active session\n/s - Active sesssions info\n"\
		     "/m <camgirl> - Model Look up in local database\n" \
		     "/a - Close all active sessions\n" \
		     "/q - Quit the program \n"
	if line[0] == '?':
		cli_out(help_string)
	elif line[0] == '/':
		if len(line) >= 2:
			if line[1] == 'h':
				cli_out(help_string)
			elif line[1]=='s':
				i = 0
				now = int(time.time())
				for session in client:
					i += 1
					newcamgirl=""
					buf="     "
					if session.new_camgirl == 1:
						newcamgirl="*NEW*"
					cli_out(fg.green+"%-05d%-10s %s (%s)%s" %
						(i, session.camgirl, newcamgirl, session.state, attr.reset))
					if session.total_tips != 0:
						buf+="Tokens          : %-05d" % session.total_tips
					if session.rank != 0:
						buf+="Rank            : %-05d " % session.rank
					if session.rank != 0 or session.total_tips != 0:
						cli_out(buf)
					cli_out("     Prem|Basic|Guest: %d|%d|%d (%d)" 
						% (session.prem, session.basics, session.guests_count, session.room_count))
                                        if session.pvt_start != 0 and session.pvt_end == 0:
                                            secs=int(time.time()) - session.pvt_start
                                            tokenspersec=1
                                            timebuf=str(datetime.timedelta(seconds=secs))
                                            buf=""
                                            if session.is_truepvt == 1:
                                                tokenspersec=80.0/60.0
                                                buf="True "
                                            tokens=secs*tokenspersec
                                            cli_out("     In %sPVT for : %s (%d tokens)" % (buf, timebuf, tokens))
					cli_out("     Active for      : %-05s(hh:mm:ss) (%s)" % (
						str(datetime.timedelta(seconds=now-session.start)), session.connected_on))
					#cli_out("     Guests added    : %-05d" % (session.guest_conn))
					#cli_out("     Chat Server     : %-s" % (session.xchat_server))
				if i == 0:
					cli_out(fg.red+"** NO ACTIVE SESSION(S) **"+attr.reset)
				cli_out("\nProgram running for  : %-05s(hh:mm:ss)" % 
					str(datetime.timedelta(seconds=now-startup_time)))
			elif line=='/lo':
				load_camgirls_list()
			elif line=='/dt':
				disable_tor()
			elif line=='/ti':
				New_tor_id()
			elif line=='/cs':
				global Cs_High
				try:
					Cs_High=int(read_input("Enter Minimum camscore to auto-connect > "))
					print "Minimum camscore set to ", Cs_High
				except:
					pass
			elif line[1]=='l':
				i = 0
				now = int(time.time())
				buf=""
				for session in client:
					if i == 0:
						session_info_header()
					i += 1
					buf+=fg.green+"%-03d %-14s %s%-9s %-6s%s" %(i, 
							session.camgirl, fg.red, "("+session.state+")", 
							str(session.cs), attr.reset)
					if i % 3 == 0:
						buf+="\n"
					else:
						buf+="\t"
				if i == 0:
					cli_out(fg.red+"** NO ACTIVE SESSION(S) **"+attr.reset)
				else:
					cli_out(buf)
				cli_out("\nProgram running for  : %-05s(hrs:mins:secs)" % 
					str(datetime.timedelta(seconds=now-startup_time)))
			elif line[1]=='j' or line[1]=='t':
				i=0
				buf=""
				for session in client:
					if i == 0:
						session_info_header()
					i += 1
					buf+=fg.green+"%-03d %-14s%s" %(i, session.camgirl, attr.reset)
					if i % 5 == 0:
						buf+="\n"
					else:
						buf+="\t"

				if i == 0:
					cli_out(fg.red+"** NO ACTIVE SESSION(S) **"+attr.reset)
					return
				else:
					cli_out(buf)
				camgirl=read_input("Model Id (1 - "+str(i)+") (0/Enter to quit)> ")
				if camgirl.isdigit() == False:
					return
				if int(camgirl) == 0:
					return
				camgirl=int(camgirl)
				if camgirl < 1 or camgirl > i:
					cli_out ("Invalid Model Id \""+str(camgirl)+"\".... :( ")
				else:
					j=1
					for session in client:
						if j==camgirl:
							if line[1]=='j':
								session.session_IO=1
								cli_out("Joined %s's room" % session.camgirl)
								session.session_input()
							elif line[1]=='t':
								session.close_session()
							return
						j += 1
			elif line[1] == 'c':
				j=1
				camgirl=read_input("Enter Model's Name > ")
				if len(camgirl) == 0:
					cli_out(fg.red+ "Not a valid username"+attr.reset)
					return
				camgirl=camgirl.strip()
				session=connect_xchat_server(camgirl, -1, 127, 0)
				if session==None:
					return
			elif line[1]=='a':
				for session in client:
					if session.state == "OFFLINE" or session.guests_count == 0 or session.joined == 0:
						if not session.camgirl.lower() in guest_lounge_camgirl:
							if session.joined == 0 or session.guests_count == 0:
								session.connection_remove_and_reconn()
							else:
								session.close_session()
			elif line[1]=='q':
				key=read_input(fg.red+"Do you really want to exit program ? <y/n> : "+attr.reset)
				if len(key) > 0 and key[0] == 'y':
					handle_signal (0,0)
			else:
				cli_out(help_string)

def read_input(prompt):
	try:
		return raw_input (prompt)
	except EOFError:
		return ""
		
def runforever():
	while True:
		line = read_input(" #> ")
		if len(line) > 0:
			try:
				process_global_commands(line)
			except Exception:
				e, t, tb = sys.exc_info()
				var = traceback.format_exc()
				print ("------------------------------------------")
				print("Exception while execute command \"%s\" : \"%s\"" % (line, t))
				print ("trace back : ", var)
				print ("------------------------------------------")


def init_default():
	global Cs_High
	global Cs_Low
	Cs_High=6000
	Cs_Low=50
        #logger = configure_logger(level=logging.INFO)
        logging.basicConfig()


def stack_trace_dump():
	print >> sys.stderr, "\n*** STACKTRACE - START ***\n"
	code = []
	for threadId, stack in sys._current_frames().items():
	    code.append("\n# ThreadID: %s" % threadId)
	    for filename, lineno, name, line in traceback.extract_stack(stack):
		code.append('File: "%s", line %d, in %s' % (filename,
							    lineno, name))
		if line:
		    code.append("  %s" % (line.strip()))

	for line in code:
	    print >> sys.stderr, line
	print >> sys.stderr, "\n*** STACKTRACE - END ***\n"

def handle_signal(signum, frame):
        stack_trace_dump()
	cli_out("Session Interrupted %d" % signum)
	main_session.close_all()
	main_session.is_running=0
	cli_out("Exiting in 10 seconds ...")
	time.sleep(10)
	main_session.stop()
	sys.exit()

def echo_test():
	cli_out (fg.green+"**************************************************************")
	cli_out ("Type /h for Help")

if __name__ == "__main__":
        print "Are we on Tor? Our IP address is : ", urllib.urlopen("http://ip.42.pl/raw").read()
	signal.signal(signal.SIGINT, handle_signal)
	init_default()
        start_mgr()
        start_cuckmgr()
	runforever()
