#!/usr/bin/env python
import subprocess
import datetime
from time import sleep
from time import time
import sys
import os
import signal
from enum import Enum

noOfSessions=0
thisSessionDate=0
currentPid=os.getpid()

#in seconds
WORK_TIME=25*60
BREAK_TIME=5*60

class nf(Enum):
	START=1
	BREAK_ST=2
	BREAK_EN=3
	WORKING=4
	TAKING_BREAK=5
	KILLED=6
	KILL_ERR=7

def send_notifcaton(c,t=0):
	global noOfSessions
	t=round(t,2)
	notfArgs=['notify-send','-t','4500','-i','/run/media/nabajit/main/workspace/programming/py/timer/Pomodoro_scr/icons/'
	,'"insert txt"','']
	if c is nf.START:
		notfArgs[5]="Start Working"
		notfArgs[4]+='work.bmp'
		notfArgs[6]=f'{noOfSessions} sessions'
	elif c is nf.BREAK_ST:
		notfArgs[5]="Take Break"
		notfArgs[4]+='break_st.bmp'
		notfArgs[6]=f'{noOfSessions+1} sessions'
	elif c is nf.BREAK_EN:
		notfArgs[5]="Break Ended"
		notfArgs[4]+='break_en.bmp'
		notfArgs[2]='0'
		notfArgs[6]=f'{noOfSessions+1} sessions'
		
	elif c is nf.WORKING:
		notfArgs[5]="Working"
		notfArgs[6]=f'{noOfSessions} sessions\n{t} min left'
		notfArgs[4]+='work.bmp'

	elif c is nf.TAKING_BREAK:
		notfArgs[5]="Taking Break"
		notfArgs[6]+=f'\n{t} min left'
		notfArgs[4]+='break_st.bmp'
		notfArgs[6]=f'{noOfSessions} sessions\n{t} min left'

	elif c is nf.KILL_ERR:
		notfArgs[5]="Error Kill"
		notfArgs[4]+='error.bmp'
		notfArgs[6]=f'{noOfSessions} sessions'

	elif c is nf.KILLED:
		notfArgs[5]="Process Killed"
		notfArgs[4]+='killed.bmp'
		notfArgs[6]=f'{noOfSessions} sessions'
		
	process = subprocess.Popen(notfArgs, stdout=subprocess.PIPE)


def get_sessions():
	global noOfSessions,thisSessionDate
	tmp=0
	date=0
	try:
		fh=open("data")
	except IOError:
		noOfSessions=0
		thisSessionDate=datetime.date.today().day
		return

	try:
		date=int(fh.readline())
	except:
		date=-1
	try:
		tmp=int(fh.readline())
	except:
		tmp=-1

	if tmp>0:
		noOfSessions=tmp;
	else:
		noOfSessions=0
	if date>0:
		thisSessionDate=date
	else:
		thisSessionDate=datetime.date.today().day
	fh.close()

def pid_exists(pid):
	try:
		os.kill(pid,0)
	except OSError:
		return False
	return True

def reset_control():
	open("control","w").close()

def write_control(x):
	global currentPid
	with open("control","w") as fh:
		fh.write(f'{x}\n{currentPid}\n{time()}')

def start_working():
	global noOfSessions,thisSessionDate
	send_notifcaton(nf.START)

	write_control('s')

	sleep(WORK_TIME)
	with open("data","w") as fh:
		if datetime.date.today().day!=thisSessionDate:
			tmpDate=datetime.date.today().day
			tmpSess=1
		else:
			tmpDate=thisSessionDate
			tmpSess=noOfSessions+1
		fh.write(f'{tmpDate}\n{tmpSess}')
	take_break()

def take_break():
	#check for already started process
	send_notifcaton(nf.BREAK_ST)
	write_control('b')
	sleep(BREAK_TIME)
	send_notifcaton(nf.BREAK_EN)
	reset_control()

#this function checks the control file for pid & process status
def control_check():
	pid=0
	status=''
	st_time=None
	if not os.path.exists('control'):
		reset_control()	
	#extract pid and status from control
	with open('control') as fh:
		status=fh.readline().strip()
		if status=='s' or status=='b':
			try:
				pid=int(fh.readline())
			except:
				pid=-1

			try:
				st_time=float(fh.readline())
			except:
				st_time=time()
		else:
			pid=-1
			
	#if arg is to kill
	if len(sys.argv)==2:
		if sys.argv[1]=='-k':
			if pid==-1:
				send_notifcaton(nf.KILL_ERR)
			else:
				try:
					os.kill(pid, signal.SIGTERM)
					send_notifcaton(nf.KILLED)
				except OSError:
					send_notifcaton(nf.KILL_ERR)
			reset_control()
			return

	#start timer
	if status=='s' or status=='b':
		if pid_exists(pid):
			if status=='s':
				send_notifcaton(nf.WORKING,(WORK_TIME-time()+st_time)/60.0)
			else:
				send_notifcaton(nf.TAKING_BREAK,(BREAK_TIME-time()+st_time)/60.0)
		else:
			start_working()
	else:
		start_working()

get_sessions()
control_check()