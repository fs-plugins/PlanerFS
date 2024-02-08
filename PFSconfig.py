from . import defconf, dat_dir, _

import re
import os
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.LocationBox import LocationBox
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from enigma import getDesktop
from Components.ActionMap import ActionMap
from Components.Label import Label
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
from time import localtime, mktime, time
from datetime import datetime,date,timedelta
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigInteger, \
	ConfigYesNo, ConfigText, ConfigClock, ConfigSelection, ConfigNumber, ConfigSubList, ConfigSequence, ConfigDirectory, \
	config, NoSave,ConfigDateTime

try:
	from Plugins.Extensions.LCD4linux.module import L4Lelement
	MyElements = L4Lelement()
	l4l=True
except:
	l4l=None

DWide = getDesktop(0).size().width()
if DWide <800:
	screen_size="SD"
elif DWide > 1300:
	screen_size="fHD"
else:
	screen_size="HD"
lt = localtime()
heute="%02i.%02i.%04i"  % (lt[2],lt[1],lt[0])    
class PlanerFSConfiguration(Screen, ConfigListScreen):


	tmpskin = open("/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/"+screen_size+"/PFSconf.xml")
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session):
		self.configparser = ConfigParser()
		self.onChangedEntry = []
		self.list = []
		self.now = [x for x in localtime()]
		self.conf=defconf
		self.conf["countdown"]=(",01.01.2024")
		self.categories=""
		self.color_list=""
		self.conf["cals_dir"]=""
		self.conf_original= self.conf
		if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
			self.configparser.read("/etc/ConfFS/PlanerFS.conf")
			if self.configparser.has_section("settings"):
				l1=self.configparser.items("settings")
				for k,v in  l1:
					if k in self.conf:
						if k=="cals_dir":
							if v.endswith("/"):
								self.conf["cals_dir"]=v
							else:
								self.conf["cals_dir"]=v+"/"
						else:
							try:
								self.conf[k] = int(v)
							except:    
								if v.lower()=="true":
									self.conf[k] = True
								elif v.lower()=="false":
									self.conf[k] = False
								else:
									self.conf[k] = v

		self.schicht=str(self.conf["schicht_art"]).split(",")
		if len(self.schicht)<4:
			self.schicht.extend(("0","0","0","Schicht")[len(self.schicht):])
		vol=self.conf["m_sound_vol"].split(",")
		self.conf["m_vol_min"]=int(vol[0])
		self.conf["m_vol_max"]=int(vol[1])
		self.now = [x for x in localtime()]
		try:
			if self.conf["starttime"] != "None":
				st=self.conf["starttime"].strip().split(':')
				self.now[3]=int(st[0])
				self.now[4] =int(st[1])
		except:
			pass

		def_Start_Time=mktime(tuple(self.now))
		cal_files = []
		sond=[dat_dir]
		cdir2=self.conf["cals_dir"]
		if cdir2 and cdir2 != "" and cdir2 != dat_dir:sond=[dat_dir,cdir2]
		for xdir in sond:
			if os.path.exists(xdir):
				for cal_file in os.listdir(xdir):
					if cal_file.endswith(".ics"):
						cal_files.append(xdir +cal_file)
		cal_files.append(("none",_("none")))
		self.altferien=self.conf["ferien"]
		self.countdown= self.conf["countdown"].split(",")
		self.cals_dir=NoSave(ConfigDirectory(default = self.conf["cals_dir"]))
		datum1=mktime(datetime.strptime(self.countdown[1], "%d.%m.%Y").timetuple())
		lim_1=[(1, 31),(1, 12),(1900, 2999)]
		self.countdown_text= NoSave(ConfigText(default=self.countdown[0], fixed_size = False))

		olddate = str(self.countdown[1]).split(".")
		self.olddate = [int(olddate[0].strip()),int(olddate[1].strip()),int(olddate[2].strip())]
		self.countdown_dat = NoSave(ConfigSequence(seperator = ".",limits=lim_1,default = self.olddate))
		self.timestartstandby = NoSave(ConfigSelection(choices = [("Yes", _("Yes")), ("No", _("No"))], default = self.conf["timestartstandby"]))
		self.timer_on = NoSave(ConfigSelection(choices = [("On", _("On")), ("Off", _("Off"))], default = self.conf["timer_on"]))
		self.ansicht = NoSave(ConfigSelection(choices = [(2, _("Big screen")),(1, _("Split screen"))], default = self.conf["ansicht"]))

		akt_i= self.conf["akt_intv"]
		if akt_i>1440:akt_i=1440
		self.akt_intv = NoSave(ConfigInteger(default = akt_i,limits = (0, 1440)))
		self.m_dauer = NoSave(ConfigInteger(default = self.conf["m_dauer"],limits = (0, 999)))
		self.m_sound = NoSave(ConfigSelection(choices = [("None", _("None")),("AUDIO", _("Audio-file")), ("radio", _("radio"))], default = self.conf["m_sound"]))
		self.m_vol_min = NoSave(ConfigInteger(default = self.conf["m_vol_min"],limits = (0, 100)))
		self.m_vol_max = NoSave(ConfigInteger(default = self.conf["m_vol_max"],limits = (1, 100)))
		self.m_radio_url = NoSave(ConfigText(default=self.conf["m_radio_url"], fixed_size = False))
		self.cal_menu = NoSave(ConfigSelection(choices = [(1, _("not extra")),(2, _("Extensionsmenu")), (3, _("Main Menu")), (4, _("Extensionsmenu")+" + " +_("Main Menu"))], default = self.conf["cal_menu"]))

		self.erinn_ext = NoSave(ConfigSelection(choices = [(0, _("No")),(1, _("Yes"))], default = self.conf["erinn_ext"]))
		self.bgr_skin = NoSave(ConfigSelection(choices = [(1, _("No")),(0, _("Yes"))], default = self.conf["bgr_skin"]))

		self.adr_menu = NoSave(ConfigSelection(choices = [(1, _("not extra")),(2, _("Extensionsmenu")), (3, _("Main Menu")), (4, _("Extensionsmenu")+" + " +_("Main Menu"))], default = self.conf["adr_menu"]))
		self.adr_on = NoSave(ConfigSelection(choices = [(0, _("No")),(1, _("Yes"))], default = self.conf["adr_on"]))
		def_start=self.conf["startanzeige2"]
		if def_start=="system start": def_start=="systemstart"
		self.startanzeige2 = NoSave(ConfigSelection(choices = [("systemstart", _("at Wakeup from Deep-Standby")), ("systemstart and time", _("at Wakeup from Deep-Standby and time")),("time", _("at time")), ("standby", _("at Wakeup from Standby(Idle)")), ("standby and time", _("at Wakeup from Standby(Idle) and time")), ("systemstart and standby", _("at Wakeup from Deep-Standby and Standby(Idle)")), ("Off", _("Off"))], default = def_start))
		self.vorschaum = NoSave(ConfigInteger(default=self.conf["vorschaum"],limits = (0, 12)))
		self.sec_file = NoSave(ConfigSelection(choices = cal_files, default = self.conf["sec_file"]))
		self.holidays_in_Startscreen = NoSave(ConfigSelection(choices = [("Yes", _("Yes")), ("No", _("No"))], default = self.conf["holidays_in_startscreen"]))
		self.doubles_in_Startscreen = NoSave(ConfigSelection(choices = [("all", _("all")), ("No", _("No")), ("if_time", _("if time"))], default = self.conf["doubles_in_startscreen"]))

		self.Start_Display_AutoHide = NoSave(ConfigInteger(default = self.conf["start_display_autohide"],limits = (0, 999)))
		self.kalender_art = NoSave(ConfigSelection(choices = [("Julian", _("Julian")),("Gregorian", _("Gregorian")), ("Off", _("Off"))], default = self.conf["kalender_art"]))
		self.altloesch_on = NoSave(ConfigSelection(choices = [("Yes", _("Yes")), ("No", _("No"))], default = self.conf["altloesch_on"]))
		self.altloesch = NoSave(ConfigInteger(default=self.conf["altloesch"],limits = (0, 999)))
		self.extern_color = NoSave(ConfigSelection(choices = [("On", _("On")), ("Off", _("Off"))], default = self.conf["extern_color"]))

		self.autosync = NoSave(ConfigSelection(choices = [("Yes", _("Yes")), ("No", _("No"))], default = self.conf["autosync"]))
		self.startscreen_plus = NoSave(ConfigYesNo(default = self.conf["startscreen_plus"]))
		self.start_back = NoSave(ConfigSelection(choices = [("no_l", _("no lines")),("lines", _("Lines"))], default = self.conf["start_back"]))

		self.l4l_on = NoSave(ConfigSelection(choices = [("Yes", _("Yes")), ("No", _("No"))], default = self.conf["l4l_on"]))
		self.l4l_lcd = NoSave(ConfigInteger(default = self.conf["l4l_lcd"],limits = (1, 5)))
		self.l4l_screen = NoSave(ConfigInteger(default = self.conf["l4l_screen"],limits = (1, 100)))
		self.l4l_font = NoSave(ConfigInteger(default = self.conf["l4l_font"],limits = (10, 999)))
		self.l4lm_font = NoSave(ConfigInteger(default = self.conf["l4lm_font"],limits = (10, 999)))
		self.l4l_ges_file = NoSave(ConfigSelection(choices = [("Yes", _("Yes")), ("No", _("No"))], default = self.conf["l4l_ges_file"]))
		self.l4l_ges_file_len = NoSave(ConfigInteger(default = self.conf["l4l_ges_file_len"],limits = (10, 999)))

		self.l_ferien = NoSave(ConfigSelection(choices = [(0, _("No")),(1, _("Yes"))], default = self.conf["l_ferien"]))
		self.startTime=NoSave(ConfigClock(default =def_Start_Time))
		self.schicht_art = NoSave(ConfigSelection(choices = [(0, _("No")),(1, _("In Calendar")+" 1"),(2, _("In Calendar")+ "2")], default = int(self.schicht[0])))
		self.schicht_onstart = NoSave(ConfigSelection(choices = [("0", _("No")),("1", _("Yes"))], default = self.schicht[1]))
		self.schicht_beschr = NoSave(ConfigSelection(choices = [("0", _("No")),("1", _("Yes"))], default = self.schicht[2]))
		self.schicht_bez = NoSave(ConfigText(default=self.schicht[3], fixed_size = False))
		Screen.__init__(self, session)
		self.skinName = "PFSconf"
		ConfigListScreen.__init__(self, [],session = session, on_change = self.reloadList)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label("Ferien")
		self["key_blue"] = Label(_("Defaults"))
		self.alt_list=[]
		self.alt_list_fix=[]
		self["help"] = Label(_("Press 'help' for explanation and 'ok' for virtual keyboard"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions","DirectionActions","HelpActions"],
			{
				"cancel": self.keyCancel,
				"ok": self.press_ok,
				"blue": self.standard,
				"green": self.okSave,
				"red": self.keyCancel,
				"yellow": self.keyFerien,
				"displayHelp": self.help1,
			}, -2
		)

		self.reloadList()
		self.setTitle("PlanerFS: " +_("Settings-Menu"))

	def standard(self):
		self.cal_menu.value=1
		self.adr_menu.value=2
		self.timer_on.value="On"
		self.m_dauer.value=0
		self.adr_on.value=1
		self.startanzeige2.value="systemstart"
		self.vorschaum.value=1
		self.holidays_in_Startscreen.value="Yes"
		self.doubles_in_Startscreen.value=_("all")
		self.sec_file.value="none"
		self.Start_Display_AutoHide.value=0
		self.kalender_art.value="Gregorian"
		self.altloesch_on.value="No"
		self.altloesch.value=365
		self.autosync.value="No"
		self.extern_color.value = "On"
		self.l4l_on.value="Yes"
		self.l4l_lcd.value=1
		self.l4l_screen.value=2
		self.l4l_font.value=40
		self.l4lm_font.value=60
		self.m_vol_min.value=10
		self.m_vol_max.value=100
		self.m_radio_url.value=""
		self.akt_intv.value=60
		self.l4l_ges_file.value="Yes"
		self.l4l_ges_file_len.value=200
		self.countdown_text.value=""
		self.countdown_dat.value= [self.now[2],self.now[1],self.now[0]]
		self.cals_dir.value=''
		self.start_back.value="no_l"
		self.conf["ferien"]="0"
		self.schicht_art.value=0
		self.schicht_onstart.value=0
		self.l_ferien.value=0

		self.reloadList()

	def press_ok(self):
		titel=None
		self.cur = self["config"].getCurrent()
		self.cur = self.cur and self.cur[1]
		if self.cur == self.m_radio_url:
			titel=_("URL for radio")
			text1= self.m_radio_url.value
		elif self.cur == self.schicht_bez:
			titel=_("Identifier text in the calendar")
			text1= self.schicht_bez.value
		elif self.cur == self.countdown_text:
			titel=_("Text for countdown display")
			text1= self.countdown_text.value
		elif self.cur == self.countdown_dat:
			titel=_("Date for countdown display")
			text1=datetime.fromtimestamp(self.countdown_dat.value).strftime('%d.%m.%Y')
		if titel:
			self.session.openWithCallback(self.texteingabeFinished,VirtualKeyBoard, title=titel, text=text1)
		elif self.cur == self.cals_dir:
			self.path_wahl(_("Set another directory for calendars"))

	def texteingabeFinished(self, ret):
		if ret is not None:
			if self.cur == self.m_radio_url:
				self.m_radio_url.value=ret
			elif self.cur == self.schicht_bez:
				self.schicht_bez.value=ret
			elif self.cur == self.countdown_text:
				self.countdown_text.value=ret
				if len(ret):
					tu=self.countdown_dat.value
					d1=date(int(tu[2]),int(tu[1]),int(tu[0]))
					if d1 <= date.today():
						d2= date.today()+timedelta(1)
						self.countdown_dat.value=[d2.day,d2.month,d2.year]
					if len(ret) and not "pd" in ret:
						self.session.open(MessageBox,_("No placeholder 'pd' for count of days in text!"),MessageBox.TYPE_ERROR)
			self.reloadList()

	def refresh(self):
		list=[]
		list.extend((
			getConfigListEntry(_("Additional directory for calendars")+" (ics)", self.cals_dir,"cals_dir"),
			getConfigListEntry(_("update every ? minutes,0=Off"), self.akt_intv,"akt_intv"),
			getConfigListEntry(_("calendar in Menu:"),self.cal_menu,"cal_menu"),
			getConfigListEntry( _("Overview-list in Menu:"),self.startscreen_plus,"startscreen_plus"), 
			getConfigListEntry(_("Background from skin"), self.bgr_skin,"bgr_skin"),
			getConfigListEntry(_("use address book:"),self.adr_on,"adr_on"),
			))
		if self.adr_on.value == 1:
			list.extend((getConfigListEntry( _("address book in Menu:"),self.adr_menu,"adr_menu"),))
		list.extend((getConfigListEntry(_("delete old events"), self.altloesch_on,"altloesch_on"),))
		if self.altloesch_on.value == "Yes":
			list.extend((
				getConfigListEntry(_("delete older than (days)"), self.altloesch,"altloesch"),
				))

		list.extend((
			getConfigListEntry(""),
			getConfigListEntry("-- "+_("overview-list")+" --"),
			getConfigListEntry(_("Setting Start"), self.startanzeige2,"startanzeige2"),
			))
		if self.startanzeige2.value != "Off":
			if self.startanzeige2.value == "time" or self.startanzeige2.value == "standby and time" or self.startanzeige2.value == "systemstart and time":
				list.extend((getConfigListEntry(_("Start-Time"), self.startTime,"starttime"),))
			if self.startanzeige2.value != "standby and time":
				list.extend((
					getConfigListEntry(_("When standby(Idle) display later"), self.timestartstandby,"timestartstandby"),
				))

			list.extend((
				getConfigListEntry(_("Months for events preview"), self.vorschaum,"vorschaum"),
				getConfigListEntry(_("Holidays in Startscreen"), self.holidays_in_Startscreen,"holidays_in_startscreen"),
				getConfigListEntry(_("Show repetitions in Startscreen"), self.doubles_in_Startscreen,"doubles_in_startscreen"),
				getConfigListEntry(_("2. File for Startscreen"), self.sec_file,"sec_file"),
				getConfigListEntry(_("Start Display AutoHide (sec, 0=Off)"), self.Start_Display_AutoHide,"start_display_autohide"),
				getConfigListEntry(_("Startscreen lines"), self.start_back,"start_back"),
				))

		list.extend((
			getConfigListEntry(""),
			getConfigListEntry("-- "+_("Timer / Reminder")+" --"),
			getConfigListEntry(_("Timer on"), self.timer_on,"timer_on"),
			))
		if self.timer_on.value=="On":
				list.extend((
			getConfigListEntry(_("Timer display time (0=endless)"), self.m_dauer,"m_dauer"),
			getConfigListEntry(_("Timer sound"), self.m_sound,"m_sound"),
			getConfigListEntry(_("Timer start volume"), self.m_vol_min,"m_vol_min"),
			getConfigListEntry(_("Timer max volume"), self.m_vol_max,"m_vol_max"),
			))
		if self.m_sound.value=="radio":
				list.extend((
					getConfigListEntry(_("radio url"), self.m_radio_url,"m_radio_url"),
					))                
		list.extend((
			getConfigListEntry(""),
			getConfigListEntry("-- "+_("extern dats")+" --"),
			getConfigListEntry(_("floating holidays"), self.kalender_art,"kalender_art"),
			))

		list.extend((getConfigListEntry(_("download on Start"), self.autosync,"autosync"),))
		list.extend((getConfigListEntry(_("extern events color in calendar"), self.extern_color,"extern_color"),))
		list.extend((getConfigListEntry(_("Show external reminders"), self.erinn_ext,"erinn_ext"),))
		list.extend((getConfigListEntry(_("Use shift plan"), self.schicht_art,"schicht_art"),))
		if self.schicht_art.value>0:
			list.extend((getConfigListEntry(" "*5+"("+_("Settings in Menu->Shift Setting...")+")"),))
			list.extend((getConfigListEntry(" "*5+_("Identifier text in calendar"), self.schicht_bez,"schicht_bez"),))
			list.extend((getConfigListEntry(" "*5+_("Show shift on startscreen"), self.schicht_onstart,"schicht_onstart"),))
			list.extend((getConfigListEntry(" "*5+_("Differentiate between: with/without description"), self.schicht_beschr,"schicht_beschr"),))
		else:
			self.schicht_onstart.value=0

		if self.conf["ferien"]:
			list.extend((getConfigListEntry("Ferien im Startscreen", self.l_ferien,"l_ferien"),))
		if l4l:
			list.extend((
			getConfigListEntry(""),
			getConfigListEntry("-- "+"LCD4Linux-Settings"+" --"),
			getConfigListEntry(_("lcd on/off"), self.l4l_on,"l4l_on"),
			))
		if self.l4l_on.value=="Yes":
			list.extend((
			getConfigListEntry(_("lcd-nr"), self.l4l_lcd,"l4l_lcd"),
			getConfigListEntry(_("lcd screen-nr"), self.l4l_screen,"l4l_screen"),
			getConfigListEntry(_("lcd list fontsize"), self.l4l_font,"l4l_font"),
			getConfigListEntry(_("lcd timer fontsize"), self.l4lm_font,"l4lm_font"),
			getConfigListEntry(_("write text file"), self.l4l_ges_file,"l4l_ges_file"),
			getConfigListEntry(_("maximum characters per line"), self.l4l_ges_file_len,"l4l_ges_file_len"),
			))
		list.extend((
			getConfigListEntry(""),
			getConfigListEntry( _("Countdown-Text:"),self.countdown_text,"cd_text"),
			))

		if len(str(self.countdown_text.value)):
			list.extend((
				getConfigListEntry(_("Info: Placeholder in text for number of days = pd")),
				getConfigListEntry(_("Countdown-Dat:"),self.countdown_dat,"cd_dat"),
				))
		else:
			self.countdown_dat.value= [self.now[2],self.now[1],self.now[0]]
		if not len(self.alt_list):
			for x in list:
				if len(x)>2:self.alt_list.append(str(x[1].value))
		self.list=list


	def reloadList(self):
		self.refresh()
		self["config"].setList(self.list)

	def keyFerien(self):
		liste=((_("Off"),1),("Baden-Wuerttemberg",3),("Bayern",2),("Berlin",5),("Brandenburg",6),("Bremen",7),("Hamburg",8),("Hessen",9),
			("Mecklenburg-Vorpommern",10),("Niedersachsen",4),("Nordrhein-Westfalen",11),("Rheinland-Pfalz",12),("Saarland",13),("Sachsen",14),
			("Sachsen-Anhalt",15),("Schleswig-Holstein",16),("Thueringen",17))
		self.session.openWithCallback(self.ferienCallback, ChoiceBox, title=_('PlanerFS - Ferien'), list=liste)

	def ferienCallback(self,cb):
		if cb:
			self.conf["ferien"]=cb[1]-1
			if cb[1]==1:
				try:
					os.remove("/tmp/1ferien.ics")
					os.remove("/tmp/2ferien.ics")
				except:
					pass

	def keyCancel(self):
		l2=[]
		for x in self.list:
			if len(x)>2:l2.append(str(x[1]))
		if self.alt_list != l2:
			self.session.openWithCallback(self.cancelConfirm,MessageBox,_("Really close without saving settings?"),MessageBox.TYPE_YESNO)
		else:
			self.close()

	def cancelConfirm(self, result):
		if result:
			self.close()

	def okSave(self):
		self.configparser = ConfigParser()
		self.configparser.read("/etc/ConfFS/PlanerFS.conf")
		if self.configparser.has_option("settings","schicht_ics"):
			self.configparser.remove_option("settings", "schicht_ics")
		if self.configparser.has_option("settings","online_on_kal"):
			self.configparser.remove_option("settings", "online_on_kal")
		schicht=','.join(str(x) for x in (self.schicht_art.value,self.schicht_onstart.value,self.schicht_beschr.value,self.schicht_bez.value))
		self.configparser.set("settings","schicht_art",schicht)
		for x in self["config"].list:
			if len(x)>2 and not x[2].startswith("schicht"):
				if x[2]=="starttime":
					st=x[1].value
					self.configparser.set("settings","starttime",str(st[0])+":"+str(st[1]))
				elif x[2]=="cd_dat":
					continue
				elif x[2]=="cd_text":
					if len(x[1].value):
						dat1=self.countdown_dat.value 
						dat2=str(dat1[0])+"."+str(dat1[1])+"."+str(dat1[2])
						st=x[1].value+","+str(dat2)
						self.configparser.set("settings","countdown","%s,%s" % (x[1].valuedat2))
					else:
						st=","+heute
						self.configparser.set("settings","countdown",",%s" % heute)
				else:
					try:
						self.configparser.set("settings",x[2],str(x[1].value))
					except:
						continue
		self.configparser.set("settings","ferien",str(self.conf["ferien"]))
		fp = open("/etc/ConfFS/PlanerFS.conf","w")
		self.configparser.write(fp)
		fp.close()

		self.save_abfrage()

	def save_abfrage(self):
		l_2=[]
		fix_list=("ansicht","extern_color")
		for x in self.list:
			if len(x)>2:l_2.append(str(x[1].value))
		if self.alt_list != l_2 or self.altferien != self.conf["ferien"]:
			self.session.open(MessageBox,_("Restart PlanerFS for new settings\nPlease wait a moment"),MessageBox.TYPE_INFO, timeout = 5)
			self.close(True,self.session,"restart")
		else:
			self.close(True,self.session)

	def help1(self):
		help=None
		cur = self["config"].getCurrent()
		cur = cur and cur[1]
		if cur == self.startanzeige2:
			help=_("When is the start screen displayed?")
		elif cur == self.countdown_text or cur == self.countdown_dat:
			help=_("for countdown in start display (pd days to christmas)")
		elif cur == self.doubles_in_Startscreen:
			help=_("Show same named appointment with all dates?")+ "\n(Startscreen, LCD4Linux)"
		elif cur == self.l_ferien:
			help=_("Ferien anzeigen in Listen?")+ "\n(Startscreen, LCD4Linux)"
		elif cur == self.vorschaum:
			help=_("How many months in advance, the dates are displayed in the startup screen?") 
		elif cur == self.holidays_in_Startscreen:
			help=_("Holidays are to be displayed in the startup screen?")
		elif cur == self.timer_on:
			help=_("For timer: off = the feature timer is off, there are no timer processed")
		elif cur == self.Start_Display_AutoHide: 
			help=_("After how many seconds to the startup screen will disappear automatically? (0 = not Auto-hide)")
		elif cur == self.kalender_art: 
			help=_("Floating holidays to Gregorian or Julian calendar to calculate or calculate off")
		elif cur==self.altloesch_on:
			help=_("If a date is copied, deleted or created, appointments can be older than they should automatically be deleted (default for days in the next step). Events with no rules that have an end-date have less than today minus default days are deleted without asking!")
		elif cur==self.altloesch:
			help=_("For example: if you enter here 365, with end-dates earlier date 365 days will be deleted.")
		elif cur==self.autosync:
			help=_("pick up the latest data automatically at startup?")
		elif cur==self.extern_color:
			help=_("colored date on the calendar for events from additional calendar files or online calendar")
		elif cur==self.l4l_ges_file:
			help=_("write /tmp/plfs_ges for 'see text file' in LCD4Linux")
		elif cur==self.l4l_ges_file_len:
			help=_("Limit line length")
		elif cur==self.ansicht:
			help=_("Show on start big or split screen")
		elif cur==self.countdown_text or cur==self.countdown_dat:
			help=_("Countdown for the start display and LCD screen, insert in the text 'pd' for the number of days")
		if help:
			self.session.open(MessageBox,help,MessageBox.TYPE_INFO)


	def callAuswahl(self, path):
		if path is not None:
			if os.path.exists(path):
				self.cals_dir.value = path
				self.reloadList()    

	def path_wahl(self, text):
		savepath = self.cals_dir.value
		self.session.openWithCallback(self.callAuswahl, LocationBox, _(text), currDir=self.cals_dir.value)
