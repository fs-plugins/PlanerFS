import os
import re
import os.path
import timer

from enigma import eTimer, eActionMap
from time import localtime, time,mktime
import datetime
from Screens import Standby
from Screens.MessageBox import MessageBox
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
timerdatei = "/etc/ConfFS/TimerFS.ics"
try:
	from Plugins.Extensions.LCD4linux.module import L4Lelement
	MyElements = L4Lelement()
	conf= {"l4lm_font" : 60,"l4l_screen" : 4,"l4l_lcd" : 1,"l4l_on" : "Yes","m_dauer" :0}
	l4l=None
	if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
		configparser = ConfigParser()
		configparser.read("/etc/ConfFS/PlanerFS.conf")
		if configparser.has_section("settings"):
			l1=configparser.items("settings")
			for k,v in  l1:
				if k in conf and v.strip() != "":   
					if v.strip() in ("False","false","None","none"):
						conf[k] = False
					elif v.strip() in ("True","true"):
						conf[k] = True
					else: 
						conf[k] = v.strip()

	if conf["l4l_on"] == "Yes": l4l=True
	l4lm_font = conf["l4lm_font"]
	l4l_lcd =  conf["l4l_lcd"]
	l4l_screen =  conf["l4l_screen"]
	alarmdauer =  conf["m_dauer"]
except:
	l4l=None

class TimerList():
	def __init__(self):
		self.timerlist=[]
		if 1==2:  
			for x in open("/tmp/pfsalert_list","r").readlines():
				if len(str(x)):    
					try:  
						wdhlg="unique"
						sound= x[4]
						aktiv="aktiv"
						if x[5]:aktiv=str(x[5])
						if x[6] and x[6] != None: wdhlg="repeat"
						if wdhlg=="unique" and datetime.date(x[3].year,x[3].month,x[3].day) < datetime.date.today():
							aktiv="no_activ"
						stunde=x[3].hour
						minute=x[3].minute
						melder = ((3600*int(stunde))+(60*int(minute)),x[0],aktiv,sound,wdhlg,x[1],x[7])
						self.timerlist.append(melder)
					except:
						pass

class Timer_dats:
	def __init__(self,Akt=None,liste=None,DPKG=None):
		self.termin_timer = eTimer()
		self.termin_timer.callback.append(self.T_Box)
		self.ti_liste=[]
		if Akt:self.from_deep(liste)

	def startTimer(self, session = None,timerliste=[],DPKG=None):
		if session is not None:
			self.session = session
			tmliste=timerliste
			if len(tmliste)>0:
				now = datetime.datetime.now()
				u = mktime(now.timetuple())
				self.timerlist2=[]
				for x in tmliste:
					self.zeitdiff=int(x[10]-u)
					if self.zeitdiff>60:
						self.timerlist2.append((self.zeitdiff,x[1],x[6],x[11],x[4],x[7],x[5]))
				self.timerlist2.sort()
				if len(self.timerlist2):
					self.Next_Termin()

	def Next_Termin(self):
		if len(self.timerlist2):   
			new_timer=self.timerlist2[0]
			self.timer_dats=self.timerlist2[0]
			if new_timer[0]>10:
				self.termin_timer.startLongTimer(new_timer[0])
			del self.timerlist2[0]

	def from_deep(self,timerdat=None):
		if timerdat:
			self.timer_dats=timerdat
			self.T_Box()

	def T_Box(self):
		startvol=10
		maxvol=100
		url=None
		url=self.timer_dats[5]
		min_anzeige=0
		sound="No"
		text=self.timer_dats[1]
		vol=self.timer_dats[2]
		sound=self.timer_dats[4]
		anz_dauer=self.timer_dats[3]
		aktiv=self.timer_dats[6]
		startvol=int(vol[0])
		self.sound=sound
		self.ex_timer = eTimer()

		import Screens.Standby

		if l4l:
			txt=_("Timermeldung")+"\n\n"+text
			s1=MyElements.getResolution(l4l_lcd)
			MyElements.add( "plFS.07.wait1",{"Typ":"wait","Lcd":str(l4l_lcd)} ) 
			MyElements.add( "plFS.08.box1",{"Typ":"box","PosX":0,"PosY":0,"Color":"red","Fill":True,"Width":s1[0],"Height":s1[1],"Screen":str(l4l_screen),"Mode":"OnMediaIdle","Lcd":str(l4l_lcd)} )
			MyElements.add( "plFS.09.txt1",{"Typ":"txt","Text":txt,"Pos":30,"Size":str(l4lm_font),"Lines":3,"Screen":str(l4l_screen),"Mode":"OnMediaIdle","Lcd":str(l4l_lcd)} )
			MyElements.setScreen(str(l4l_screen),str(l4l_lcd))


		from .PFSanzeige import Timermeldung
		if Screens.Standby.inStandby:
			eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.rcKeyPressed)
			if aktiv=="sb" or aktiv=="dsb":
				self.vol_down(startvol)
				Screens.Standby.inStandby.Power()
				from Tools import Notifications
				Notifications.AddNotification(Timermeldung,text,anz_dauer,sound,vol,url,None)
			else:
				if not os.path.exists("/tmp/plfst1"):
					Standby.inStandby.onHide.append(self.T_Liste)
		else:
			self.vol_down(startvol)
			self.session.open(Timermeldung,text,anz_dauer,sound,vol,url,None)
		self.Next_Termin()

	def vol_down(self,startvol):
		if self.sound=="radio" or self.sound=="AUDIO":
			from enigma import eDVBVolumecontrol,eServiceReference, iRecordableService
			volctrl = eDVBVolumecontrol.getInstance()
			volctrl.setVolume(startvol,startvol)

	def l4l_exit(self):
		MyElements.delete( "plFS.07.wait1")
		MyElements.delete( "plFS.08.box1")
		MyElements.delete( "plFS.09.txt1")
		MyElements.setScreen("0","1")

	def rcKeyPressed(self, key, flag):
		if l4l and str(key)=="352":
			self.l4l_exit()

	def T_Liste(self):
		if os.path.exists("/tmp/plfst1"):
			fp = file('/tmp/plfst1', 'r')
			t_lines = fp.readlines()
			fp.close()
			text="verpasste Timer-Meldungen:\n\n"
			for x in t_lines:
				text=text+x+"\n"
			from Tools import Notifications
			Notifications.AddNotification(MessageBox, text, type=MessageBox.TYPE_INFO)
			os.unlink("/tmp/plfst1")

	def restart(self, session = None,tm_liste=[],DPKG=None):
		self.termin_timer.stop()
		if len(tm_liste):
			self.startTimer(session,tm_liste)