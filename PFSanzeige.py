from . import my_version,defconf, _

from Screens.Screen import Screen
from Screens.InfoBarGenerics import InfoBarNotifications
from Components.ActionMap import ActionMap
from GlobalActions import globalActionMap
from Components.Label import Label
from Components.Sources.List import List
from enigma import eServiceReference, eTimer
from enigma import getDesktop
from time import localtime, strftime
import datetime
import os.path
from enigma import eDVBVolumecontrol
from Components.VolumeControl import VolumeControl
from skin import parseColor
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
from enigma import iPlayableService
from Components.ServiceEventTracker import ServiceEventTracker 
 
try:
	from Plugins.Extensions.LCD4linux.module import L4Lelement
	MyElements = L4Lelement()
	l4l=True
except:
	l4l=None

allcolor_list=("#00008B","#D2691E","#006400","#696969","#FFD700","#000000","#B22222","#8B8878","#CD0000","#00868B","#f0f8ff","#ff4500","#20343c4f","#deb887","#228B22","#5F9EA0","#DC143C","#F0F8FF","#EEC900","#20343c4f","#f0f8ff")

class FehlerAnzeige(Screen, InfoBarNotifications):
	ALLOW_SUSPEND = True
	skin = """
	<screen position="center,center" size="400,150" title="%s" >
		<eLabel text="PlanerFS" position="0,5" zPosition="4" size="400,25" font="Regular;24" valign="center" halign="center" transparent="1" />
		<widget name="text1" position="0,40" zPosition="4" size="400,25" font="Regular;22" valign="center" halign="center" transparent="1" />
		<eLabel text="(/etc/configFS/PlanerFS.ics)" position="0,65" zPosition="4" size="400,25" font="Regular;22" valign="center" halign="center" transparent="1" />
		<widget name="text2" position="0,100" zPosition="4" size="400,25" font="Regular;22" valign="center" halign="center" transparent="1" />
	</screen>"""  % "PlanerFS: "

	def __init__(self, session,err_meld):
		Screen.__init__(self, session)
		self["text1"] = Label(err_meld)
		self["text2"] = Label(_("Break execution"))
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.close,
			"cancel": self.close,
		})

class Timermeldung(Screen, InfoBarNotifications):
	ALLOW_SUSPEND = True
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/timermeldung.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/timermeldung.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/timermeldung.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session, text="",anz_dauer=0,sound=None,vol=(10,100),url=None,DPKG=None):
		self.conf=defconf
		self.m_dauer=0
		configparser = ConfigParser()   
		configparser.read("/etc/ConfFS/PlanerFS.conf")
		if configparser.has_section("settings"):
			l1=configparser.items("settings")
			for k,v in  l1:
				if k=="m_dauer":
					self.m_dauer=v
		Screen.__init__(self, session)
		self.skinName="Timermeldung"
		InfoBarNotifications.__init__(self)
		self.maxvol = vol[1]
		self.startvol = vol[0]
		self.url=url
		self["text1"] = Label(_("Event is due!"))
		self["text2"] = Label(text)
		self.text=text
		self.timer1 = eTimer()
		self.volume_timer = eTimer()
		self.ex_timer = eTimer()
		self.timer1.timeout.get().append(self.klang)
		self.volume_timer.timeout.get().append(self.vol_plus)
		self.sound_on=False
		try:
			if int(self.m_dauer)>0:
				self.ex_timer.timeout.get().append(self.exit)        	
				self.ex_timer.startLongTimer(self.m_dauer)
		except:
			pass
		self["actions"] = ActionMap(["OkCancelActions","GlobalActions"],
		{
			"ok": self.ok_press,
			"cancel": self.ok_press,
			"volumeDown": self.vol_down,
			"volumeUp": self.vol_up,
		})

		self.onClose.append(self.anzeige_exit)

		self.setTitle("PlanerFS\n" +_("Timers message!"))
		self.sounder=0
		if sound=="AUDIO" or sound=="radio":
			self.oldvol = eDVBVolumecontrol.getInstance().getVolume()
			self.sounder=1
			self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
			self.musicfile="/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/PFSsound.mp3"
			if sound=="radio" and self.url:
					self.musicfile=self.url
			else:
				self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
					{
					iPlayableService.evEOF: self.__schleife,
					})
			self["text1"].setText(_("radio alarm Clock"))
			self.onLayoutFinish.append(self.klang)

	def ok_press(self):
		if self.volume_timer.isActive():
			self.volume_timer.stop()
		else:
			self.close()
	def vol_down(self):
		if self.volume_timer.isActive(): 
			self.volume_timer.stop()
		VolumeControl.instance.volDown()
	def vol_up(self):
		if self.volume_timer.isActive(): 
			self.volume_timer.stop()
		VolumeControl.instance.volUp()
	def vol_plus(self):
		oldvol2 = eDVBVolumecontrol.getInstance().getVolume()
		if oldvol2 < self.maxvol:
			VolumeControl.instance.volUp()
			self.volume_timer.startLongTimer(20)


	def klang(self):
		if self.sound_on == False:
			sref = eServiceReference(4097, 0, self.musicfile)
			self.session.nav.playService(sref)
			self.sound_on=True
			if self.maxvol: self.volume_timer.startLongTimer(20)

	def __schleife(self):
		self.sound_on=False
		self.session.nav.playService(self.oldService)
		self.timer1.startLongTimer(15)




	def anzeige_exit(self):
		if self.ex_timer.isActive():
			self.ex_timer.stop()
			if l4l:
				MyElements.setScreen("0","1")
				MyElements.delete( "plFS.08.box1")
				MyElements.delete( "plFS.09.txt1")
		if self.sounder==1:
			self.session.nav.stopService()
			eDVBVolumecontrol.getInstance().setVolume(self.oldvol,self.oldvol)
			self.session.nav.playService(self.oldService)
			self.timer1.stop()

	def exit(self):
		eDVBVolumecontrol.getInstance().setVolume(self.oldvol,self.oldvol)
		self.close(True)




class startscreen8(Screen, InfoBarNotifications):
	ALLOW_SUSPEND = True
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/startscreen.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/startscreen.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/startscreen.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session, terminliste):
		self.categories1=(_('Birthday'),_('Anniversary'),_('Wedding day'),'Birthday','Anniversary','Wedding day')
		self.z_liste=("0","1","1","0","1","1","0","0","0","0")
		self.conf=defconf
		self.conf["countdown"]=(",01.01.2024")
		self.conf["cat_color_list"]=[]
		self.conf["doubles_in_startscreen"]="all"
		configparser = ConfigParser()   
		configparser.read("/etc/ConfFS/PlanerFS.conf")
		if configparser.has_section("settings"):
			l1=configparser.items("settings")
			for k,v in  l1:
				if k=="cat_color_list":
					self.conf[k]=v.split(",")
				elif k=="z_liste":
					self.z_liste=list(v.split(","))
				elif k=="categories":
					categories1=v#.encode("UTF-8")
					self.categories1= list(categories1.split(","))
				else:
					try:
						self.conf[k] = int(v)
					except:
						self.conf[k] = v
		if len(self.conf["cat_color_list"])<21:
			self.conf["cat_color_list"].extend(allcolor_list[len(self.conf["cat_color_list"]):])
		self.term_list=terminliste
		Screen.__init__(self, session)
		self.skinName="startscreen8"
		InfoBarNotifications.__init__(self)
		lt = localtime()
		self["listlabel"] = List([])#self.listlabel
		self["titel"] = Label(_("Upcoming calendar events"))
		self["version"] = Label(my_version)
		self["greentext"] = Label("OK")
		self["yellowtext"] = Label(_("Calendar"))
		self["countdown"] = Label()
		self["dat1"] = Label(_(strftime("%A"))+", "+strftime("%d.%m.%Y"))#+_(strftime("%m"))+strftime(" %Y"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.exit,
			"cancel": self.exit,
			"green": self.exit,
			"yellow": self.kalender
		})
		if self.conf["start_display_autohide"] > 0:
			self.off_timer = eTimer()
			self.off_timer.timeout.get().append(self.close)
			self.off_timer.startLongTimer(self.conf["start_display_autohide"])
		self.onLayoutFinish.append(self.make_list)
		self.setTitle("PlanerFS"+_("Date display"))

	def make_list(self):
		self["countdown"].hide()
		if self.conf["countdown"]:
			if len(self.conf["countdown"].split(","))==2:
				countd = self.conf["countdown"].split(",")
				tu = datetime.datetime.strptime(str(countd[1]), "%d.%m.%Y")
				cd_date=datetime.date(tu.year,tu.month,tu.day)-datetime.date.today()
				if cd_date.days>0:
					self["countdown"].setText(countd[0].replace("pd",str(cd_date.days)))
					self["countdown"].instance.setBackgroundColor(parseColor(self.conf["cat_color_list"][12]))
					self["countdown"].show()

		start_back=self.conf["start_back"]
		listnew=self.term_list
		double_list=[]

		color = int(self.conf["cat_color_list"][20].lstrip('#'), 16) 
		rot =int(self.conf["cat_color_list"][16].lstrip('#'), 16)
		color_inactiv =int(self.conf["cat_color_list"][15].lstrip('#'), 16)
		color_ue =int(self.conf["cat_color_list"][18].lstrip('#'), 16)

		cal_bg =int(self.conf["cat_color_list"][19].lstrip('#'), 16)
		if start_back=="lines":
			self["listlabel"].style = "lines"

		alist=[]
		ges_list=[]
		geblist=[]
		termlist=[]
		warnlist=[]
		datum1=""
		ft=None
		if self.conf["holidays_in_startscreen"]== "Yes":
			ft= _("HOLIDAY").lower()
		for x in listnew:
			doub=1
			if len(x)>11 and x[11]:doub=None
			if x[2] and ((x[2]==_('HOLIDAY') and self.conf["holidays_in_startscreen"] !="Yes") or x[2]=='timer'):
				doub=None
			if (doub and self.conf["doubles_in_startscreen"] !="all"):
				check=(x[1],x[6])
				ttm=0
				if self.conf["doubles_in_startscreen"] =="if_time" and (x[6] and isinstance(x[6][0],int)):ttm=x[6][0]+x[6][1]
				if ttm==0 and check in double_list:
					doub=0
				else:    
					double_list.append(check)
			elif len(x)>12 and x[12]:
				check=(str(x[3])+str(x[12]),x[1])
				if check in double_list:
					doub=0
				else:    
					double_list.append(check)

			if (len(termlist)+len(warnlist))<20:  
				if doub:
					d=x[9]
					akt=0
					if (x[6] != (0,0) and d >= datetime.datetime.today()) or (x[9].date() >= datetime.date.today()):
						color2 =color
						color1 = color
						alter2=""
						jubi=None
						categories=str(x[2]).lower()
						d_check=_(d.strftime("%a"))+d.strftime(", %d.%m.")
						zeit=""
						if len(x)>12 and x[12]:
							zeit = "- "+ x[12].strftime(" %d.%m. ")
						elif x[6][0]+x[6][1]>0:
							zeit='%s%0.2d:%0.2d ' %(x[6][2],x[6][0],x[6][1])

						such= str(x[1])+str(x[2])+str(x[5])

						cat_ind=None
						for tmp in self.categories1:
							if categories and categories.lower().strip() == tmp.strip().lower() or tmp.strip().lower() in such.lower():     #.upper()
								jubi = tmp.strip()
								cat_ind= self.categories1.index(tmp) #+=1
								break
							else:
								if tmp.strip() in such:
									jubi = tmp.strip()
									break

						if jubi:
							if ft and jubi == ft:
								color2 = int(self.conf["cat_color_list"][11].lstrip('#'), 16) #color_list[11]

							elif cat_ind and self.z_liste[cat_ind]=="1":  
								alter = int(x[8])
								if alter>0:
									if alter % 10 == 0:
										color1 = rot
									elif alter % 5 == 0:
										color1 = rot
									alter2=' ('  + str(alter) + ')'

							if x[4] == 1:
								y=(d_check,zeit+x[1]+alter2,color1,0)
								if len(alter2):
									geblist.append(y)
								else:
									termlist.append(y)
							else:    
								y=(d_check,zeit+x[1]+ alter2, color1,4,color2)  #+ tmp + ", "
								warnlist.append(y)

						else:
							if x[4] == 1:            
								y=(d_check,zeit+x[1],color1,0)
								termlist.append(y)                                                
							else:
								y=(d_check,zeit+x[1],color1,4,color2)
								warnlist.append(y)

			else:
				break
#ENDE: fuer Geburts- und Jahrestage, Farbe festlegen und alter bestimmen
		ges_list.append((1,_("Events for today")+":",color_ue,1,""))
		if termlist:
				ges_list.extend(termlist)
		else:
				ges_list.append((2,_("No Events registered for today"),color_inactiv,0))

		if geblist:
				ges_list.append((3,_("Anniversaries today:"),color_ue,1))
				ges_list.extend(geblist)
		else:
				ges_list.append((4,_("No anniversary registered for today"),color_inactiv,0))

		ue_text = _("Next events:")
		ges_list.append((5,"",cal_bg,1))
		ges_list.append((6,ue_text,color_ue,1))
		ges_list.extend(warnlist)
		vor=""
		for x in ges_list:
				res = [] 
				if x[3]==1: 
					vor=" "*2
					res=(vor+x[1]," ",vor+x[1],x[2],cal_bg)
				if x[3]==4:
					vor=" "*2
					if len(x)>3:vor=" "*5
					res=(vor+x[0],x[1],vor+x[0]+"\t"+x[1], color,cal_bg)
				elif x[3]==0:
					vor=" "*5
					res=(vor+x[1]," ",vor+x[1],x[2],cal_bg)
				alist.append(res)

		while len(alist)<20:
				alist.append(("","","",color, cal_bg)) 
		self["listlabel"].setList(alist)


	def kalender(self):
		self.close(self.session,True) 


	def exit(self):                
		self.close(None)#(self.session) 


class playing:
	def __init__(self, session, musicfile):
		sref = eServiceReference(4097, 0, musicfile)
		self.session.nav.playService(sref)
