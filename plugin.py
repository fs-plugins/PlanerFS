################################################################################
# PlanerFS
# 
#   (beginn 24.10.2010)
#
#   Enigma2 Plugin
#
#  Author: shadowrider  (fs-plugins)
#
##########################
from . import my_version,dat_dir,defconf, _

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
import Screens.Standby
from Screens import Standby

from Tools import Notifications
from Tools.Directories import copyfile, fileExists

from Components.config import config
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser

from enigma import eTimer

from time import localtime, time, strftime, mktime
import datetime
import os

txt="Version: "+my_version+"\n"
try:
	import cPickle as pickle
except ImportError:
	import pickle

try:
	from Plugins.Extensions.LCD4linux.module import L4Lelement
	L4L=L4Lelement()#True
	from PFSl4l import l4l_export
except Exception as e:
	L4L=None
	txt+="No L4L\n"

try:
	if not fileExists("/etc/ConfFS/PlanerFS.ics"):
		ret = copyfile("/usr/lib/enigma2/python/Plugins/Extensions/sample_PlanerFS/sample.ics","/etc/ConfFS/PlanerFS.ics")
	if not fileExists("/etc/ConfFS/PlanerFS.vcf"):
		ret = copyfile("/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/sample.vcf","/etc/ConfFS/PlanerFS.vcf")
except:
	pass

from .timer import Timer_dats
from .routines import schicht, modul, readfiles
from .termin import TerminList
from .PFSimport import online_import


systemstart=0
display_size=None
plfs_list=[]
conf=defconf

l4l_sets=[1,1,40]
plfstimer_list=[]
plfs_list=[]
configparser = ConfigParser()
if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
	configparser.read("/etc/ConfFS/PlanerFS.conf")
	if configparser.has_section("settings"):
		l1=configparser.items("settings")
		for k,v in  l1:
			if k=="l4l_lcd": 
				l4l_sets[0]=int(v)
			elif k=="l4l_screen": 
				l4l_sets[1]=int(v)
			elif k=="l4l_font": 
				l4l_sets[2]=int(v)
			elif k=="cals_dir":
				if v.endswith("/"):
					conf["cals_dir"]=v
				else:
					conf["cals_dir"]=v+"/"
			else:  
				try:
					conf[k] = int(v)
				except:
					conf[k] = v
		if str(conf["version"]) != my_version:
			configparser.read("/etc/ConfFS/PlanerFS.conf")
			configparser.set("settings", "version",my_version)
			conf["version"]=my_version
			file1=open('/etc/ConfFS/PlanerFS.conf',"w")
			configparser.write(file1)
			file1.close()
	else:
		pass


else:
	datei=open('/etc/ConfFS/PlanerFS.conf',"w")
	configparser.add_section("settings")
	for k,v in conf.items():
		configparser.set("settings", k,v)
	configparser.write(datei)
	datei.close()

onl_lines=[]
if os.path.exists('/etc/ConfFS/PlanerFS_online.txt'):
	with open('/etc/ConfFS/PlanerFS_online.txt', 'r') as fp:
		onl_lines = fp.readlines()

else:
	fp=open("/etc/ConfFS/PlanerFS_online.txt","w")
	fp.write("##internetadressen fuer online-Kalender\n# Aufbau:\n##    name = url = calendarNr\n##sample (delete # / entferne #) :\n")
	fp.write("\n#Feiertage_Germany = https://calendar.google.com/calendar/ical/de.german%23holiday%40group.v.calendar.google.com/public/basic.ics\n")
	fp.close()

time_timer=Timer_dats(None,None,None)
global akt_intv
if int(conf["akt_intv"]):
	akt_intv=int(conf["akt_intv"])
	if akt_intv > 1440: akt_intv=1440
	akt_intv=akt_intv*60
else:
	akt_intv=0

cal_menu = conf["cal_menu"]
adr_menu = conf["adr_menu"]
adr_on = conf["adr_on"]
startscreen_plus = conf["startscreen_plus"]


class sofort():
	def __init__(self,liste=None):
		if liste:  
			e1=self.session.open(Timer_dats,1, d_start,None)

class einlesen():
	def __init__(self,r=None):
		if r:
			global plfstimer_list
			global plfs_list
			fer=None
			if str(conf["l_ferien"]) != "0":fer=(conf["ferien"],conf["l_ferien"])
			hmex=[]
			termine=[]
			timer=[]
			fehler=[]
			schichten=[]
			erg=1
			allfiles = readfiles(self,True,conf["cals_dir"])
			if conf["autosync"]=="Yes":
				path='/etc/ConfFS/PlanerFS_online.txt'
				#if conf["cals_dir"] != '/etc/ConfFS/' and os.path.exists(conf["cals_dir"]+'PlanerFS_online.txt'):
				#	path=conf["dat_dir"]+'PlanerFS_online.txt'
				erg=online_import().run(path,fer,1)
				if erg==0 and not Screens.Standby.inStandby:
					Notifications.AddNotification(MessageBox, "PlanerFS\n"+_("Error: at least one external file could not be loaded!"), type=MessageBox.TYPE_ERROR, timeout = 30)


			files=[]
			if conf["kalender_art"] != "Off":
				files.append("kalender")
			if conf["sec_file"] != "" and conf["sec_file"] != _("none") and os.path.exists(conf["sec_file"]):
				files.append(conf["sec_file"])
			files.extend(allfiles)
			fileliste=[]
			if len(files):
				for file1 in files:
					if file1 not in fileliste and os.path.exists(file1):
						fileliste.append(file1)
						listen2=TerminList().t_read(0,file1,modul)#.listen7
						if listen2 and len(listen2):termine.extend(listen2[0])
						timer.extend(listen2[1])
						if len(listen2)==4:
							schichten.extend(listen2[3])

			if erg and str(conf["schicht_send_url"]) and len(schichten):
				schicht1=schicht().parseSchicht(schichten,"export1")
				nl2=""
				if schicht1 and len(schicht1):
					anz=len(schicht1)
					for i2 in range(anz):
						sh1=schicht1[i2]
						nt=sh1[1].replace(" ","%20")
						if nt==None or nt=="":
							nt="frei"
						nl2+=sh1[3].strftime('%d.%m.%Y')+","+nt+";"    
				opt = ' -O /dev/null'
				ur=str(conf["schicht_send_url"])+nl2
				com = 'wget "' + ur + '"' + opt
				f=open("/tmp/schicht","w")
				f.write(strftime("%d.%m.%y %H:%M:%S" ,localtime())+" send schichtdaten\n")
				f.close()
				os.system(com)


			if L4L is not None and len(schichten):
				from .PFSpaint import mspFS_paint
				mspFS_paint(schichten)
			if len(termine):termine.sort(key=lambda x:x[9])
			plfstimer_list=timer
			plfs_list=termine


class Termin_Timer():
	def __init__(self):
		self.session = None
		self.erstmal=0
		self.aktual_timer = eTimer()
		self.startzeit_timer=None
		self.display_timer = None
		self.MyElements = None
		self.pfsstandby=False

	def saveSession(self, session):
		self.session = session


	def standby_on(self):
		if Screens.Standby.inStandby:
			self.pfsstandby=False
			Standby.inStandby.onHide.append(self.Days)
		else:
			if not self.pfsstandby:
				self.pfsstandby=True
				config.misc.standbyCounter.addNotifier(self.standby_start, initial_call = False)

	def standby_start(self, configElement):
		self.pfsstandby=False
		self.standby_check_timer1.startLongTimer(60)

	def Starter(self):
		if time()<1383701983:
			self.sttimer = eTimer()
			self.sttimer.timeout.get().append(self.datecheck)
			self.sttimer.startLongTimer(2)
		else:
			self.Starter2()

	def datecheck(self):
		if time()<1383701983:
			self.sttimer = eTimer()
			self.sttimer.timeout.get().append(self.datecheck)
			self.sttimer.startLongTimer(2)
		else:
			self.Starter2()

	def Starter2(self):
		start_s=conf["startanzeige2"].replace("(idle)","")
		global systemstart
		self.standby_check_timer1=None
		if self.startzeit_timer:
			self.startzeit_timer.stop()
			self.startzeit_timer=None
		self.run_timer=None
		if not os.path.exists('/etc/ConfFS/PlanerFS.ics'):
			f=open('/etc/ConfFS/PlanerFS.ics',"w")
			f.write("BEGIN:VCALENDAR\nMETHOD:PUBLISH\nPRODID: -EnigmaII-Plugin / PlanerFS "+my_version+"\nVERSION:2.0")
			f.write("\nEND:VCALENDAR")
			f.close()

		a=einlesen(1)
		if akt_intv>0:
			self.aktual_timer.timeout.get().append(self.aktual)
			self.aktual_timer.startLongTimer(akt_intv)

		if conf["timer_on"] =="On":
			if len(plfstimer_list):
				global time_timer
				time_timer=Timer_dats(None,None,None)
				time_timer.startTimer(self.session,plfstimer_list,None)
		if start_s != "None" and "time" in start_s: 
			st=conf["starttime"].strip().split(':')
			sek=((int(st[0])*60)+int(st[1]))
			now = [x for x in localtime()]
			sek2=((now[3]*60)+now[4])
			start=(sek-sek2)*60
			self.startzeit_timer = eTimer()
			self.startzeit_timer.timeout.get().append(self.Days1)
			if start<0:
				start = start+86400
			elif start<20:
				start=86400-start
			self.startzeit_timer.startLongTimer(start) 

		if "systemstart" in start_s:
			if systemstart==0:  
				self.Days()
				systemstart=1
		if "standby" in start_s: 
			self.standby_check_timer1 = eTimer()
			self.standby_check_timer1.timeout.get().append(self.standby_on)
			self.standby_check_timer1.startLongTimer(60)
			self.standby_on()
		else:
			pass
		if L4L is not None and conf["l4l_on"]=="Yes":
			self.l4l()

	def Days1(self):
		if Screens.Standby.inStandby:
			if conf["timestartstandby"]=="Yes" and conf["startanzeige2"] !="standby and time":
				Standby.inStandby.onHide.append(self.Days)
			else:
				self.Days()


	def Days(self):
		if self.standby_check_timer1:
			self.standby_check_timer1.startLongTimer(60)
		if len(plfs_list):
			from .PFSanzeige import startscreen8
			Notifications.AddNotificationWithCallback(check_re,startscreen8, plfs_list)


	def aktual(self):
		einlesen(1)
		if str(conf["timer_on"]) =="On":
			time_timer.restart(self.session,plfstimer_list,None)
		if L4L and conf["l4l_on"]=="Yes":
			self.l4l()
		z=datetime.datetime.today()
		end=datetime.datetime(z.year,z.month,z.day,0,0,2)+ datetime.timedelta(1)
		diff=end-z
		next2=diff.seconds
		if next2>akt_intv and akt_intv>0:
			next2=akt_intv
		self.aktual_timer.startLongTimer(next2)


	def l4l(self):
		global L4L
		global display_size
#		self.MyElements = L4Lelement()
#		if self.MyElements is None:
#			try:
#				from Plugins.Extensions.LCD4linux.module import L4Lelement
#				self.MyElements = L4Lelement()
#			except:
#				L4L=None
		if L4L is not None:
#			self.MyElements = L4Lelement()
			self.display_timer = eTimer()
			self.display_timer.timeout.get().append(self.l4l)
			if display_size>0:
				if self.display_timer:
					self.display_timer.stop()
					self.display_timer = None
				if len(plfs_list)>0:
					from .PFSl4l import PFS_l4l
					a= PFS_l4l(plfs_list,l4l_sets,conf["vorschaum"],display_size)
			elif display_size==0:
				display_size=L4L.getResolution(l4l_sets[0])[1]
				self.display_timer.startLongTimer(2)
			else:
#				if self.MyElements is None:
#					from Plugins.Extensions.LCD4linux.module import L4Lelement
#					self.MyElements = L4Lelement()
				display_size=L4L.getResolution(l4l_sets[0])[1]
				self.display_timer.startLongTimer(2)


if modul==0:
	txt+="no icalendar-modul\n"
if len(txt):
	f=open("/tmp/PlanerFS-Errors.txt","w")
	f.write(txt)
	f.close()
	txt=""
t_timer=Termin_Timer()

def uebersicht(session, **kwargs):
		from .PFSanzeige import startscreen8
		session.openWithCallback(check_re,startscreen8, plfs_list)

def main(session, **kwargs):
	from .PlanerFS import PlanerFS7 as PlanerFS
	session.openWithCallback(check_re,PlanerFS)

def check_re(session=None, *args):
	if session and args:
		main(session)

def adress(session, **kwargs):
	if adr_on:
		from .PFSCards import PFS_show_card_List7
		session.openWithCallback(check_re,PFS_show_card_List7,None)

def adress_menu(menuid, **kwargs):
	if adr_on:
		if menuid == "mainmenu":
			return [(_("PlanerFS address book"), adress, "PlanerFS address book", 58)]
		return []

def pfs_wecker(session, **kwargs):
	from .PFSwe import PFS_show_we
	session.open(PFS_show_we)

def pfs_wecker2(**kwargs):
	begin = -1
	if len(plfstimer_list):
		if os.path.exists('/etc/ConfFS/PlanerFS.ics'):
			l2=TerminList().t_read(1,'/etc/ConfFS/PlanerFS.ics',modul)#.listen7
			tim_list=l2[1]
			tim_list.sort(key=lambda x:x[10])
			for x in tim_list:
				if x[10]+(config.recording.margin_before.value * 60)> time():
					pickle.dump(x,open("/media/hdd/plfs_dstart", 'wb'),1)
					begin= x[10]+(config.recording.margin_before.value * 60)+(x[11]*60)
					break
	return begin

def calen_menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("PlanerFS"), main, "PlanerFS", 57)]
	return []

def autostart(**kwargs):
	if "session" in kwargs:
		session = kwargs["session"]
		t_timer.saveSession(session)
	t_timer.Starter()

def Plugins(**kwargs):
	pfc_list=[PluginDescriptor.WHERE_PLUGINMENU]
	pfa_list=[PluginDescriptor.WHERE_PLUGINMENU]
	if cal_menu==2 or cal_menu==4:
		pfc_list.append(PluginDescriptor.WHERE_EXTENSIONSMENU)
	if adr_on==1 and (adr_menu==2 or adr_menu==4):
		pfa_list.append(PluginDescriptor.WHERE_EXTENSIONSMENU)
	list=[PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart, wakeupfnc = pfs_wecker2),
		PluginDescriptor(name="PlanerFS", where=pfc_list, icon="PlanerFS.png", description=_("Schedule appointments, view events"), fnc=main)]
	if adr_on==1:
		list.append(PluginDescriptor(name=_("PlanerFS address book"),description=_("addresses and phone numbers search, find, manage, and more"), where = pfa_list,icon="PlanerFS_adr.png",fnc = adress))
	if startscreen_plus =="True":
		list.append(PluginDescriptor(name=_("PlanerFS overview"), where=pfc_list, icon="PlanerFS.png", description=_("Show start screen with overview"), fnc=uebersicht))
	if cal_menu==3 or cal_menu==4:
		list.append(PluginDescriptor(name="PlanerFS", where=PluginDescriptor.WHERE_MENU, fnc=calen_menu))
	if adr_on==1 and (adr_menu==3 or adr_menu==4):
		list.append(PluginDescriptor(name="PlanerFS address book", where=PluginDescriptor.WHERE_MENU, fnc=adress_menu))
	list.append(PluginDescriptor(name="PlanerFS alarm clock", where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=pfs_wecker))

	return list 