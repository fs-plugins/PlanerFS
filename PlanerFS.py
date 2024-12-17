# -*- coding: utf-8  -*-
###############################################################################
#
# PlanerFS von shadowrider
# Chrashlogs, Vorschlaege, Beschwerden usw. bitte an plugins@fs-plugins.de senden
#
################################################################################
from . import my_version, DWide, dat_dir, defconf, _

from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen

from Tools.LoadPixmap import LoadPixmap

try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser

from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Label import Label
from Components.FileList import FileList
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel

from skin import parseColor, parseFont
from time import localtime, strftime, strptime
import datetime

from enigma import eTimer,ePoint, eSize

import os
import re
import os.path

try:
	from Plugins.Extensions.Fritzcall.plugin import FritzCallFBF
	fbf = FritzCallFBF
except ImportError:
	fbf = None

from .PFSconfig import PlanerFSConfiguration
from .PFScateg import PFS_categorie_conf7
from .PFSEdit import PFS_edit_Termin
from .routines import Feiertage, Rules, Next_Termin, Farben,schicht, modul, readfiles

msp_liste=()
try:
	from Plugins.Extensions.mspFS.exporter import exporter
	msp=True
except:
	msp=False

conf=defconf
categories1=[] 
color_list=[]
z_liste=conf["z_liste"]#("0","1","1","0","1","1","0","0","0","0")
days=(_("Monday"),_("Tuesday"),_("Wednesday"),_("Thursday"),_("Friday"),_("Saturday"),_("Sunday"))

allcolor_list=["#00008B","#D2691E","#006400","#696969","#FFD700","#000000","#B22222","#8B8878","#CD0000","#00868B","#f0f8ff","#ff4500","#20343c4f","#deb887","#228B22","#5F9EA0","#DC143C","#F0F8FF","#EEC900","#20343c4f","#f0f8ff","#000000","#ffffff"]
screen_size="HD"
if DWide < 730:
	screen_size="SD"
elif DWide >1300:
	screen_size="fHD"

termindatei = "/etc/ConfFS/PlanerFS.ics"
termindatei_2 = ""
if os.path.isfile("/etc/ConfFS/PlanerFS2.ics"):
	termindatei_2 = "/etc/ConfFS/PlanerFS2.ics"
cal_files_path="/etc/ConfFS"
lt = localtime()
###############################################################################		

class PlanerFS7(Screen, HelpableScreen):
	def __init__(self, session):
		global conf
		global z_liste
		global color_list
		global categories1
		global cal_bg,color_inactiv,rot,weiss
		zus=""
		configparser = ConfigParser()
		configparser.read("/etc/ConfFS/PlanerFS.conf")
		if configparser.has_section("settings"):
			l1=configparser.items("settings")
			for k,v in  l1:
				if k == "schicht_col":
					conf["schicht_col"]= v
				elif k.strip() == "kalender_art":
					conf["kalender_art"] = v
				if k=="categories":
					cat_categories=v
					categories1=list(cat_categories.split(","))
				elif k=="cat_color_list":
					cat_color_list=v
					color_list= list(cat_color_list.split(","))
				elif k=="z_liste":
					z_liste=list(v.split(","))
				else:
					try:
						conf[k] = int(v)
					except:    
						conf[k] = v
		if len(color_list)<23:
			color_list.extend(allcolor_list[len(color_list):])
		if len(categories1)<10:
			categories1=(_("None"),_("Birthday"), _("HOLIDAY"), _("Anniversary"), _("Wedding day"),_("None"),_("None"),_("None"),_("None"),_("None"))
		self.schichtnamen=None
		self.show_schichttermin=False
		self.kalnum=1
		schicht=str(conf["schicht_art"]).split(",")
		if len(schicht)<4:
			schicht.extend(("0","0","0","Schicht")[len(schicht):])
		conf["schicht_art"]=int(schicht[0])
		if conf["schicht_art"]:
			if not isinstance(conf["schicht_col"], dict):
				conf["schicht_col"]=eval(conf["schicht_col"])
			self.schichtnamen=[]
			if isinstance(conf["schicht_col"], dict):
				for key in conf["schicht_col"].keys():
					self.schichtnamen.append(key)
			self.schicht_bez=schicht[3]
		if len(color_list)<21:
			color_list.extend(allcolor_list[len(color_list):]) 
		cal_bg=Farben().farb_re(color_list[12])
		color_inactiv= Farben().farb_re(color_list[15])
		rot = Farben().farb_re(color_list[16])
		weiss = Farben().farb_re(color_list[17])
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/"+screen_size+"/PlanerFS.xml"
		tmpskin = open(skindatei)
		self.skin = tmpskin.read()
		tmpskin.close()

		self.session = session
		self.cards_on=False
		self.extern_color=conf["extern_color"]
		self.kalender_art = conf["kalender_art"]
		self.bgr_skin = conf["bgr_skin"]

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = "PlanerFS7"
		self.menutitle=""
		wt=[(_("WN"),_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Su"))]
		self["weekdays"]= List([])
		self["weekdays"].setList(wt)
		self["event_list"] = List([])
		self["calendar"] = List([])
		self["kwlist"] = List([])
		self["greena_1"] = Pixmap()
		self["greena_2"] = Pixmap()
		self["greena_2"].hide()                
		self["errs"] = Pixmap()
		self["errs"].hide()
		self["help"] = ScrollLabel("")
		#self["help"].hide()
		self.hlp=None
		self.ed_list=["New event",()]
		self.sel_dat=0
		self.min_dat=0
		self.list_site=0
		self.eigen_events = []
		self.schichtlist=[]
		self.color_holiday=color_list[11]
		self.color_days=color_list[10]
		self.cal_background=color_list[12]
		self.color_event=color_list[13]
		self.color_today=color_list[14]
		self.categories=categories1
		self.TitelTimer = eTimer()
		self.msp_liste=None
		if hasattr(self.TitelTimer, 'callback'):
			self.TitelTimer.callback.append(self.setDatum)
		else:
			self.TitelTimer_conn = self.TitelTimer.timeout.connect(self.setDatum)
		self.edit_index=None
		self["event_list"].onSelectionChanged.append(self.changed)
		self["event_list"].style = "notselected"
		self["descreption"] = Label("")
		self["titel"] = Label("PlanerFS - "+my_version)
		self.setTitle("PlanerFS - "+my_version)
		self["datum"] = Label('%0.2d.%0.2d.%0.4d %0.2d:%0.2d %s' %(lt[2],lt[1],lt[0],lt[3],lt[4]," "*2)) 
		self["kal_num"] = Label(" "*5+_("cal.1"))
		self["ueberschrift"] = Label("")
		self["key_yellow"] = Label(_("Timer"))
		self["key_green"] = Label(_("Update data"))
		self["key_red"] = Label(_("Terminlist"))
		self["key_blue"] = Label(_("Today"))
		self["list_titel"] = Label(_("Terminlist"))

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
		{
			"cancel": (self.exit,_("Close PlanerFS")), 
			"ok": (self.edit_termin,_("Edit selected Termin")),
			}, -2)
		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"yellow": (self.yellow,_("Show timer")),
			"red": (self.red,_("Toggle Calender/Terminlist")),
			"green": (self.green,_("Update data")), #internet import
			"blue": (self.blue,_("Show current month")),  #zum aktuellen Monat
			}, -2)

		self["DirectionActions"] = HelpableActionMap(self, "DirectionActions",
		{
			"left": self.left,
			"right": self.right,
			"down": self.down,
			"up": self.up,
			}, -2)
		BQ1=[(self.Bouquet, _("Change calendar file")),(self.Bouquet,_("Change calendar file"))]
		if termindatei_2=="":BQ1=[(self.rueck,_("previous month")),(self.vor,_("next Month"))]
		eakt_dict={"prevBouquet": BQ1[0],"nextBouquet": BQ1[1],"prevService": BQ1[0],"nextService": BQ1[1]}
		if conf["adr_on"]:
			eakt_dict["info"]=(self.vcards,_("Show buisness card of selected name"))
		eakt_dict["input_date_time"]=(self.showMainMenu,_("Show more Options in Menu"))
		self["EPGSelectActions"] = HelpableActionMap(self, "EPGSelectActions",eakt_dict, -2)

		self["MenuActions"] = HelpableActionMap(self, "MenuActions",
			{
				"menu": (self.showMainMenu, _("PlanerFSMenu"))
			}
		)
		self["MediaPlayerActions"] = HelpableActionMap(self, "MediaPlayerActions",
			{
				"previous": (self.rueck,_("previous month")),
				"next": (self.vor,_("next Month")),
				"subtitles": (self.vcards_list,_("Open adress book")),
			}, -1)
		self["MediaPlayerSeekActions"] = HelpableActionMap(self, "MediaPlayerSeekActions",
			{
			"seekFwd": (self.vor,_("next Month")),
			"seekBack": (self.rueck,_("previous month")),
			}, -1)

		self.today=datetime.date.today()
		altdat=datetime.datetime.today()-datetime.timedelta(conf["altloesch"])
		self.altdat=datetime.datetime(altdat.year,altdat.month,altdat.day,23,59,59)
		self.monat=lt[1]
		self.jahr=lt[0]

		self.terminfile=termindatei
		if self.monat==12:
			sdt1=datetime.date(self.jahr+1, 1, 1)-datetime.timedelta(1)
		else:
			sdt1=datetime.date(self.jahr, self.monat+1, 1)-datetime.timedelta(1)
		self.monatstage=int(sdt1.day)
		self.onLayoutFinish.append(self.start_set)

	def setDatum(self):
		lt = localtime()
		self["datum"].setText('%0.2d.%0.2d.%0.4d %0.2d:%0.2d %s' %(lt[2],lt[1],lt[0],lt[3],lt[4]," "*2))
		self.TitelTimer.startLongTimer(60) 

	def start_set(self):
		self.TitelTimer.startLongTimer(60)
		self["help"].instance.setZPosition(999)
		self["help"].hide()
		if self.bgr_skin:
			self.instance.setBackgroundColor(parseColor(self.cal_background))
			self["descreption"].instance.setBackgroundColor(parseColor(self.cal_background))
			self["ueberschrift"].instance.setBackgroundColor(parseColor(self.cal_background))
			self["list_titel"].instance.setBackgroundColor(parseColor(self.cal_background))
		if str(conf["ferien"]) != "0":
			from .PFSimport import online_import
			online_import().run(dat_dir,(conf["ferien"],conf["l_ferien"]),None)
		self.einlesen()
  
	def info_ical(self):
		self.session.open(MessageBox, _("no icalendar import from system possible\nplease ask in the forum to the image how it can be installed"), MessageBox.TYPE_INFO)


	def vcards(self):
		if (conf["adr_on"]):
			if not os.path.exists('/etc/ConfFS/PlanerFS.vcf'):
				datei=open('/etc/ConfFS/PlanerFS.vcf',"w")
				datei.close()
			if self["event_list"].getCurrent() is not None:
				name_x = self["event_list"].getCurrent()[3][1]
				geb= self["event_list"].getCurrent()[3][3]
				geb2= str(geb.year) +"-" + str(geb.month)+"-"+str(geb.day)
				try:
					self.session.open(PFS_show_card7,name_x,geb2)
				except:
					from .PFSCards import PFS_show_card7
					self.session.open(PFS_show_card7,name_x,geb2)
	def vcards_list(self):
		if (conf["adr_on"]):
			if not os.path.exists('/etc/ConfFS/PlanerFS.vcf'):
				datei=open('/etc/ConfFS/PlanerFS.vcf',"w")
				datei.close()
			if os.path.exists('/etc/ConfFS/PlanerFS.vcf'):
				try:
					self.session.open(PFS_show_card_List7,"cal_on")
				except:
					from .PFSCards import PFS_show_card_List7
					self.session.open(PFS_show_card_List7,"cal_on")


	def showMainMenu(self):
		menu = []
		if self.hlp:
			self.hlp=None
			self["help"].hide()
		if self.list_site==1:
			if self["event_list"].getCurrent():
				if self["event_list"].getCurrent()[3]:
					extern=self["event_list"].getCurrent()[3][11]
					self.session.openWithCallback(self.menuCallback, PanerFS_menu7, extern)
			else:
				self.session.openWithCallback(self.menuCallback, PanerFS_menu7, 1)
		else:
			self.session.openWithCallback(self.menuCallback, PanerFS_menu7, 9)

	def menuCallback(self,menu_nr):
		if menu_nr is not None and menu_nr !="nix":
			if menu_nr=="fileHandling":
				self.fileHandling()
			elif menu_nr=="edit_termin":
				self.edit_termin()
			elif menu_nr=="delete_termin":
				self.delete_termin()
			elif menu_nr=="new_termin":
				self.new_termin()
			elif menu_nr=="config_start":
				self.config_start()
			elif menu_nr=="config_colors":
				self.config_colors()
			elif menu_nr=="import_termin":
				self.edit_termin()
			elif menu_nr=="Online_cal":
			    self.online_cals()
			elif menu_nr=="Adress_cards" and conf["adr_on"]:
				self.vcards_list()
			elif menu_nr=="about":
				self.showAbout()
			elif menu_nr=="info_ical":
				self.info_ical()
			elif menu_nr=="Shift dates":
				if self.show_schichttermin:
					self.show_schichttermin=False
				else:
					self.show_schichttermin=True
				self.einlesen()
			elif menu_nr=="Setting_shifts":
				from .PFScateg import schicht_conf
				self.session.open(schicht_conf)
			elif menu_nr=="show_errors":    
				text=""
				if os.path.exists('/tmp/PlanerFS-Errors.txt'):
					if os.path.getsize("/tmp/PlanerFS-Errors.txt")>60:
						fp = open("/tmp/PlanerFS-Errors.txt")
						text = fp.read()
						fp.close()
					else:
						text=_("congratulation! no errors found") 
				else:
					try:
						fp = open("/tmp/PlanerFS-Errors.txt","w")
						fp.close()
						text="/tmp/PlanerFS-Errors.txt does not exist, new add this file"
					except Exception as e:
						text="/tmp/PlanerFS-Errors.txt does not exist and cannot be created"
						if e and len(str(e)):
							text=text+"\n\n"+str(e)
				self["help"].setText(text)
				self["help"].show()
				#self["help"].instance.setZPosition(6)
				self.hlp=1

	def showAbout(self,args=None):
		text2 = '\n\n'+'Autor: shadowrider' + '\nhttps://github.com/fs-plugins/PlanerFS'
		if modul:
			text2+="\n\niCalendar ok"
		else:
			text2+"\n\nno iCalendar installed"
		self.session.open(MessageBox,"planerFS - Version "+ my_version +text2, MessageBox.TYPE_INFO)

	def online_cals(self):
		from .PFSonl import PlanerFSonline_files
		self.session.openWithCallback(self.einlesen, PlanerFSonline_files)

	def fileHandling(self):
		from .PFSfiles import PFS_filemenu7
		self.session.openWithCallback(self.einlesen, PFS_filemenu7)

	def Bouquet(self):
		if self.kalnum==1:
			self.kalnum=2
			self["kal_num"].setText(_("cal.2"))
		else:
			self.kalnum=1
			self["kal_num"].setText(_("cal.1"))
		self["descreption"].setText("")
		self.einlesen()

	def red(self):
		lt=self["list_titel"].getText().replace(_(" (active)"),"")
		if self.list_site==0:
			self.list_site=1
			self["event_list"].style = "default"
			self.changed()
			self["key_red"].setText(_("Calendar"))
			self["list_titel"].setText(lt+_(" (active)"))
			self["greena_1"].hide()
			self["greena_2"].show()
		else:
			try:
				self["ueberschrift"].setText("<<   " +self.monatsname+" "+str(self.jahr)+"   >>")
			except:
				pass
			self["descreption"].setText("")
			self["list_titel"].setText(lt)
			self["event_list"].style = "notselected"
			self.list_site=0 
			self.showActiveDat()
			self["key_red"].setText(_("Terminlist"))  
			self["greena_2"].hide()
			self["greena_1"].show()
			self["list_titel"].show()

	def green(self):    #liste alle dat-Termine bilden und senden
		from .PFSimport import online_import
		erg=online_import().run(dat_dir+'PlanerFS_online.txt',(conf["ferien"],9),1)
		if erg==0:
			self.session.open(MessageBox, _("Error: at least one external file could not be loaded!")+"\n/tmp/PlanerFS_Errors.txt", MessageBox.TYPE_ERROR) 
		elif erg==2:
			self.session.open(MessageBox, _("Successfully loaded data"), MessageBox.TYPE_INFO)   
			self.schichtfile=None
			self.einlesen()

	def einlesen(self):    #planerFS-iCal Datei einlesen
		self.testdat=''
		dataLines = []
		ica=None
		self.events = []
		self.eigen_events = []
		self.schichtlist=[]
		self.events2 = []
		ica3=None
		modu2=1
		fileList = readfiles(self,True,conf["cals_dir"])
		if len(fileList) > 0:
			ica=[]
			ica2=[]
			fl=[]
			for item in fileList:
				if not item in fl: 
					nam=item
					fl.append(nam)
					if os.path.isfile(nam): 
						if modul:
							parse1 = Rules().parseEvent_b(nam,self.schichtnamen)
							if parse1:
								tx_tsr= dat_dir+"2"
								modu2=None
								if  "PlanerFS2.ics" in nam or tx_tsr in nam:
									ica2.extend(parse1)
								else:
									ica.extend(parse1)
							else:
								modu2=1
						if modu2:
							tempFile = open(nam, 'r')
							dataLines.append("filename:" +str(item))
							dataLines.extend(tempFile.readlines())
							tempFile.close()
			if ica:
				self.readEvents1(ica,1)
				if len(ica2):
					self.readEvents1(ica2,2) 
			if len(dataLines):
				self.readEvents(dataLines)
		else:
			self.liste_anzeigen()

	def readEvents1(self, ica, num=1):
		check=[]
		for x in ica:
			ch2=str((x[0],x[2]))
			if ch2 not in check:
				check.append(ch2)
				if conf["schicht_art"] and x[14]:
					in1=None
					if "PlanerFS.ics" in str(x[9]) or "PlanerFS2.ics" in str(x[9]):
						in1=x
						self.eigen_events.append(x)
						if self.show_schichttermin:
								self.events.append(x)
					self.schichtlist.append((x[0],x[2],x[3],x[5],x[6],in1,x[17]))
				else:
					if "PlanerFS.ics" in str(x[9]) or "PlanerFS2.ics" in str(x[9]):
						self.eigen_events.append(x)
					if num==2:
						self.events2.append(x)
					else:
						self.events.append(x)
		self.bew_feiert()
		self.liste_anzeigen()

	def readEvents(self, lines):
		mask = {}
		mask['BEGIN'] = re.compile("^BEGIN:VEVENT")
		mask['END'] = re.compile("^END:VEVENT")
		inEvent= False
		index=0
		rname=""
		art="event"
		fname=None
		fname2=""
		for line in lines:
			if 'filename' in line:
				fname=str(line).replace("filename:/etc/ConfFS/","")
				rname=fname
			if "X-WR-CALNAME" in line:
				fname2=str(line).replace("X-WR-CALNAME:","")                        
			if mask['BEGIN'].match(line):
				eventLines = []
				inEvent = True
			elif mask['END'].match(line) and inEvent:
				if not fname:
					fname=fname2
				parse1 = Rules().parseEvent(eventLines,index,fname,self.schichtnamen) 
				if parse1:
					in1=None
					if "PlanerFS.ics" in rname or "PlanerFS2.ics" in rname:
						self.eigen_events.append(parse1)
					if conf["schicht_art"] and parse1[14]:
						in1=None
						if "PlanerFS.ics" in rname or "PlanerFS2.ics" in rname:
							in1=parse1
							if self.show_schichttermin:
								self.events.append(parse1)
						self.schichtlist.append((parse1[0],parse1[2],parse1[3],parse1[5],parse1[6],in1,parse1[17]))
						
					else:
						if  "PlanerFS2.ics" in rname or conf["cals_dir"]+"2" in rname:
							self.events2.append(parse1)
						else:
							self.events.append(parse1)
						index+=1
				inEvent = False
			elif inEvent:
				eventLines.append(line)
		self.bew_feiert()
		self.liste_anzeigen()


	def liste_anzeigen(self):
		global msp_liste
		eventliste3=[]
		self.feiertagsliste=[]
		self.term_liste=[]
		self.term_liste5=[]
		self.termcol_liste=[]
		self.cat_term_liste=[]
		self.timerliste=[]
		index=-1
		self.timer=0
		jetzt=(self.jahr,self.monat)
		if self.kalnum==1:
			alist=self.events
		else:
			alist=self.events2
		for x in alist: 
			zaehler=0
			if x[1] and x[1].upper() == "TIMER": 
				continue
			next_datet=None
			next_datet = Next_Termin().next_termin(x[5], x[2], x[3],jetzt,1,"planer", x[17])
			zeit=(x[2].hour,x[2].minute)
			zeit2=(x[3].hour,x[3].minute)
			zeitges=1
			if zeit[0]+zeit[1]+zeit2[0]+zeit2[1]==0:
				zeit=None
				zeit2=None
				zeitges=None
			elif zeit == zeit2: 
				zeit2=None
			repeat=0
			for next_date in next_datet:
				if len(str(next_datet))>2:
					if x[5]==None:
						repeat=repeat+1
						if zeitges and x[3].date()>x[2].date():
							zeit=None
							zeit2=None
							if next_date==x[2]:
								zeit=(x[2].hour,x[2].minute)
							elif next_date.date()==x[3].date():
								zeit2=(x[3].hour,x[3].minute)
					color=None
					eigen_num=2
					if  x[9] == "PlanerFS.ics" or x[9] == "PlanerFS2.ics":
						eigen_num=0
					if len(x)>16:
						y=(next_date,x[0],x[1],x[2],x[3],x[4],x[5],self.jahr,x[6],x[7],x[8],eigen_num,x[9],x[10],zeit,index,zaehler,x[12],zeit2,x[13],repeat,x[11],x[15],x[16],x)
					else:
						y=(next_date,x[0],x[1],x[2],x[3],x[4],x[5],self.jahr,x[6],x[7],x[8],eigen_num,x[9],x[10],zeit,index,zaehler,x[12],zeit2,x[13],repeat,x[11],None,None,x)
					index+=1
					
					eventliste3.append(y)
					categories=str(x[1])
					hd=_("HOLIDAY")
					#hd=str.encode(hd)
					if self.extern_color=="On" or eigen_num==0:
						if x[1] and hd in x[1]:# != -1:
							self.feiertagsliste.append(next_date.day)
						cat_ind=0
						for tmp in categories1:
							if categories and tmp.strip() in categories:
								color=color_list[cat_ind]
								break
							cat_ind+=1
						if not color:
							testtext=str(x[0])+str(x[6])
							for c in categories1:
								if c.strip() in testtext:
									color=color_list[categories1.index(c)]
									break
						self.term_liste.append(datetime.date(next_date.year,next_date.month,next_date.day))
						self.term_liste5.append((datetime.date(next_date.year,next_date.month,next_date.day),x[0]))
						self.termcol_liste.append(color)
						zaehler+=1
			index+=1
		if self.kalender_art != "Off":
			self.bew_feiert()
			for x in self.bewegl_feiertage:
				next_date=None
				next_datet= Next_Termin().next_termin(x[5], x[2], x[3],jetzt,1,"planer2")
				next_date=next_datet
				for next_date in next_datet:
					y=(next_date,x[0],x[1],x[2],x[3],None,None,self.jahr,x[6],0,None,1,"br",None,None,None,None,None,None,None,0,None,None,None)
					eventliste3.append(y)
					self.feiertagsliste.append(next_date.day)
		eventliste3.sort()
		monatsnamen = (_("January"),_("February"),_("March"),_("April"),_("May"),_("June"),_("July"),_("August"),_("September"), _("October"),_("November"),_("December"))
		self.monatsname=monatsnamen[self.monat-1]
		self.timer=0
		l_1=[]
		for x in eventliste3:
			if len(x)<=16 or x[16]==0:
				l_1.append(x)
		self.eventliste3=eventliste3
		l_2=[]
		for x in eventliste3:
			if x[2]!="TIMER" and (len(x)>20 and x[20]<2):
				color1 = weiss #0xFFFFFF #Farbe bei Nichtauswahl
				color2 = weiss
				color5 = weiss
				color6 = weiss
				res = [ x ]
				abst1=60
				text= str(x[1])
				alter1=""
				jubi=0
				dat1='%0.2d.' %int(x[0].day)
				dat2=""
				rd=None
				if x[4].date() > x[3].date():
					rd=1
				if int(x[4].month) != int(x[0].month):
					dat2 = ' (- %0.2d.%0.2d.)' % (int(x[4].day),int(x[4].month))
				else:
					dat2 = ' - %0.2d.' %int(x[4].day) 
					abst1=130
				if rd:
					dat1=dat1+dat2
				else:
					if len(x)>14:
						zeit=""
						zeit2=""
						if x[14]:zeit=' %0.2d:%0.2d ' %(x[14][0],x[14][1])
						if x[18]:zeit2='- %0.2d:%0.2d ' %(x[18][0],x[18][1])
						if len(zeit+zeit2):
							dat1=dat1+" "+zeit+zeit2
							abst1=120
				dat1=dat1+" "*2
#fuer Geburts- und Jahrestage, Farbe festlegen und alter bestimmen
				cattxt=str(x[2])+str(x[8])#.upper()
				if _('HOLIDAY').lower() in cattxt.lower():
					color5 = rot #datum rot wenn feiertag
					color6 = rot
					text = text+' ('+ (_('HOLIDAY'))+')'
				else:
					tmp_al=0
					cat_ind=0
					for tmp in categories1:
						if cattxt and tmp.strip() in cattxt:
							if z_liste[cat_ind]=="1":
								tmp_al=1
							break
						cat_ind+=1
					if tmp_al==1:
						alter = x[7] - int(x[3].year)
						alter1 = ' (' + str(alter) + ')'
						ha=None
						if "dogage" in x[8].lower() and alter>0:
							if alter == 1:
								ha = 14
							elif alter == 2:
								ha = 22
							elif alter > 2:
								ha= 22 + (alter -2)*5 
							if ha:alter1 = ' (' + str(alter) + " **"+str(ha)+ ')'
						if alter % 10 == 0:
							color1 = rot
							color2 = rot
						elif alter % 5 == 0:
							color1 = 0x87CEEB
							color2 = 0x87CEEB
						else:
							color1 = weiss
							color2 = weiss 
						text = text+alter1
				if x[9]>0:
					text = text+' (' + (_('Date Error'))+')'
				#ENDE: fuer Geburts- und Jahrestage, Farbe festlegen und alter bestimmen
				text= " "+dat1+" "+text
				if x[11] != 0 and x[11] != 3:
					text = "*" +text
				else:
					text = " " +text
				l_2.append((text, color1, color2,x))
		self["event_list"].setList(l_2)
		self.setTitle(self.monatsname+" "+str(self.jahr))
		self["ueberschrift"].setText("<<   " +self.monatsname+" "+str(self.jahr)+"   >>")
		msp_liste=[]
		if (conf["schicht_art"]==1 and self.kalnum==1) or (conf["schicht_art"]==2 and self.kalnum==2):
			if len(self.schichtlist):   
				msp_liste=schicht().parseSchicht(self.schichtlist,jetzt,"s1")
			elif msp:
				msp_liste=exporter((self.jahr,self.monat)).w_list
			if len(msp_liste) and len(msp_liste[0])>3:msp_liste.sort(key=lambda x:x[3])
		i=1
		ir=0
		kwliste=[]
		d1=datetime.date(self.jahr,self.monat,1)
		d2=d1.weekday()
		dt_list=[[],[],[],[],[],[],[]]
		sel=0
		self.min_dat=None
		for x in range(42):
			terms=[]
			if (x+7)%7==0:
				ir+=1
				b_col=""
			if self.cal_background:
				b_col=self.cal_background
				f_col=self.color_days
			if x >= d2 and i <= self.monatstage:
				sel +=1
				if not self.min_dat:self.min_dat=x-1
				r=datetime.datetime(self.jahr,self.monat,i)
				wn1=r.isocalendar()[1]
				if wn1 and not wn1 in kwliste:
					kwliste.append(wn1) 
				if datetime.date(self.jahr,self.monat,i).weekday() == 6:
					f_col=self.color_holiday
				if i in self.feiertagsliste:
					f_col=self.color_holiday
				if datetime.date(self.jahr,self.monat,i) in self.term_liste:
					for term in self.term_liste5:
						if term[0]== datetime.date(self.jahr,self.monat,i):
							terms.append(term[1])
					b_col=self.color_event
					if self.termcol_liste[self.term_liste.index(datetime.date(self.jahr,self.monat,i))]:
						b_col=self.termcol_liste[self.term_liste.index(datetime.date(self.jahr,self.monat,i))]
				if  datetime.date(self.jahr,self.monat,i) == datetime.date.today():
					b_col=self.color_today
				dt_list[ir].append((str(i),f_col,b_col,terms))
				i=i+1
			else:
				dt_list[ir].append(("",f_col,self.cal_background,terms))
		if self.sel_dat ==0: self.sel_dat = datetime.date.today().day
		self.d_list = dt_list
		self.d2list = []
		msp_list=[]
		for dat in dt_list:
			d_test=0
			self.d3list = []
			msp_t_list=[]
			if len(dat):
				for x in dat:
					if len(x):
						txt=str(x[0])
						if txt=='':
							txt=" "
						else:
							d_test=d_test+int(x[0])
						if conf["schicht_art"] and len(msp_liste):
							try:
								if len(x[0]):
									tp=msp_liste[int(x[0])-1]
									ext_color=Farben().farb_re(tp[2])
									msp_t_list.append(" ",ext_color,tp[1])
								else:
									msp_t_list.append(" ",Farben().farb_re(self.cal_background),tp[1]) 
							except:
								pass
						self.d3list.append(txt)
						self.d3list.append(Farben().farb_re(x[2]))
						self.d3list.append(Farben().farb_re(x[1])) 
						if txt ==" ":
							self.d3list.append(Farben().farb_re(self.cal_background))
						elif int(self.sel_dat) == int(x[0]):
							self.d3list.append(0xffffff)
						else:
							self.d3list.append(0x000000)
				if d_test>0:
					self.d2list.append(tuple(self.d3list))
					if conf["schicht_art"] and len(msp_t_list):msp_list.append(tuple(msp_t_list))
		self["calendar"].style = "default"
		self["calendar"].setList(self.d2list)
		if not os.path.exists('/tmp/PlanerFS-Errors.txt'):
			fx=open("/tmp/PlanerFS-Errors.txt","w")
			fx.write("errors-text wurde vor dem Start durch Fremdeinwirkung geloescht!\n\nDadurch sind Fehler in den Routinen nicht erkennbar")
			fx.close()
		elif os.path.getsize("/tmp/PlanerFS-Errors.txt")>60:
			self["errs"].show()
		self["help"].hide()
		self.setKW(kwliste)
		self.showActiveDat()

	def setKW(self,kwliste):
		list1 = []
		for wn in kwliste:
			text= '%0.2d' %wn
			#list1.append((text,0))
			list1.append((text,Farben().farb_re(color_list[21]),Farben().farb_re(color_list[22])))
		self["kwlist"].setList(list1)

	def termin_liste_anzeigen(self):
		timerliste2=[]
		index=0
		for x in self.events:
			if x[1] and x[1].upper()=="TIMER":
				if x[3]:
					stunde=x[2].hour
					minute=x[2].minute
				eigen=1
				minu=(stunde*60)+minute
				if x[9] == "PlanerFS.ics" or x[9] == "PlanerFS2.ics":
					eigen=0
				y=(minu,x[0],x[1],x[2],x[3],x[4],x[5],self.jahr,x[6],x[7],x[8],eigen,x[9],x[10],None,index,None,x[12],None,x[13],None,x[11],x[15],x)
				timerliste2.append(y)                    
			index+=1
		timerliste2.sort()
		l_2=[]
		for x in timerliste2:
			text= x[1].replace('\\n',', ')
			color1 = weiss
			color2 = weiss 
			aktiv =""
			if x[13] and x[13]=="no_activ":
				color1 = color_inactiv
				color2 = color_inactiv
			etime='%0.2d:%0.2d' %(x[3].hour,x[3].minute)
			text=" "+etime+" "+text
			if x[11] != 0 and x[11] != 3:
				text = "* " +text
			l_2.append((text, color1, color2,x))
		self.timer=1
		self["event_list"].setList(l_2)
		self.setTitle("Timer-Liste")

########################################################################
# abarbeitung ob termin angezeigt wird


	def bew_feiert(self):
		self.bewegl_feiertage=()
		if self.kalender_art=="Gregorian":
			self.bewegl_feiertage=Feiertage().ostern_greg(self.jahr) 
		elif self.kalender_art=="Julian":    
			self.bewegl_feiertage=Feiertage().ostern_jul(self.jahr)
		else:
			pass

	def vor(self):
		if self.monat==12:
			self.monat=1
			self.jahr=self.jahr+1
		else:
			self.monat=self.monat+1
			if self.monat==12:
				sdt1=datetime.date(self.jahr+1, 1, 1)-datetime.timedelta(1)
			else:
				sdt1=datetime.date(self.jahr, self.monat+1, 1)-datetime.timedelta(1)
			self.monatstage=int(sdt1.day)
		if self.monat==1:
			self.bew_feiert()
		self["descreption"].setText("")
		self.sel_dat=1
		self.liste_anzeigen()

	def rueck(self):
		sdt1=datetime.date(self.jahr, self.monat, 1)-datetime.timedelta(1)
		self.monatstage=int(sdt1.day)
		if self.monat==1:
			self.monat=12
			self.jahr=self.jahr-1
		else:
			self.monat=self.monat-1
			self.jahr=self.jahr
		if self.monat==12:
			self.bew_feiert()
		self["descreption"].setText("")
		self.sel_dat=self.monatstage
		self.liste_anzeigen()

	def blue(self): 
		self.today=datetime.date.today()
		self.monat=lt[1]
		self.jahr=lt[0]
		if self.monat==12:
			sdt1=datetime.date(self.jahr+1, 1, 1)-datetime.timedelta(1)
		else:
			sdt1=datetime.date(self.jahr, self.monat+1, 1)-datetime.timedelta(1)
		self.monatstage=int(sdt1.day)
		self.bew_feiert()
		self["descreption"].setText("")
		self.sel_dat = datetime.date.today().day
		self.liste_anzeigen()


	def changed(self):
		kat=""
		if self["event_list"].getCurrent() is not None:
			index = self["event_list"].getCurrent()[3]
		if self["event_list"].getCurrent():
			descreption = ""
			datum=""
			zeit=""
			location=""
			kat=""
			descreption = str(self["event_list"].getCurrent()[3][8]).replace("dogage","")
			if descreption is None or not len(descreption):
				descreption= self["event_list"].getCurrent()[3][1]                   
			elif self["event_list"].getCurrent()[3][1] not in descreption:
				descreption = self["event_list"].getCurrent()[3][1]+", "+descreption 
			descreption =descreption.replace('\n',', ').replace('\\',' ')
			kat1= str(self["event_list"].getCurrent()[3][2])
			if self["event_list"].getCurrent()[3][2]: kat1= str(self["event_list"].getCurrent()[3][2])
			if not kat1 or kat1 =="" or kat1 =="None":
				for tmp in categories1:
					if tmp.strip() in descreption:
						kat1= tmp.strip()
						descreption =descreption.replace(tmp.strip(),"")
			alter=""
			if kat1 and len(kat1) and kat1 !="None" and kat1 != _("None"):
				cat_ind=0
				for tmp in categories1:
					tmpstrip=tmp.strip()
					if kat1 and kat1 in tmpstrip:
						if z_liste[cat_ind]=="1":
							alter = " "+str(index[7] - int(index[3].year))
							break
						cat_ind+=1
					kat = " (" + _(str(kat1))+ alter+")"
			date = self["event_list"].getCurrent()[3][0]
			if self.timer==0:
				kompl=self["event_list"].getCurrent()[3]
				day=date.weekday()
				day_name = days[day]
				datum=day_name+", " '%0.2d' %int(date.day)+". " + self.monatsname
				if len(kompl)>19 and kompl[19]:
					if len(str(kompl[19])):
						location= ", "+kompl[19]
					descreption =datum+zeit+": " +descreption+location + kat 
			self["descreption"].setText(str(descreption))

	def yellow(self,):
		if self.list_site==0:
			self.list_site=1
			self["event_list"].style = "default"
			self["greena_1"].hide()
			self["greena_2"].show()
			self["key_red"].setText(_("Calendar"))
		if self.timer==0:
			self.termin_liste_anzeigen()
			self["key_yellow"].setText(_("Events"))
			self["list_titel"].setText(_("Timer")+" (active)")
			self["ueberschrift"].setText(self.monatsname+" "+str(self.jahr))
		else:
			self.liste_anzeigen()
			self["ueberschrift"].setText(self.monatsname+" "+str(self.jahr))
			self["key_yellow"].setText(_("Timer"))
			self["list_titel"].setText(_("Terminlist")+" (active)")


	def left(self,num=None):
		if self.list_site==1: 	
			self["event_list"].pageUp() 
		else:
			if self.sel_dat == 1:
				self.rueck()
			else:
				self.sel_dat -= 1
				self.showActiveDat()

	def right(self,num=None):
		if self.list_site==1: 	
			self["event_list"].pageDown() 
		else:
			if self.sel_dat >= self.monatstage:
				self.vor()
			else:
				self.sel_dat += 1
				self.showActiveDat()

	def up(self,num=None):
		if self.list_site==1: 	
			self["event_list"].selectPrevious() #.up() 
		else:
			if self.sel_dat == 1:
				self.rueck()
			else:
				self.sel_dat -= 7
				if self.sel_dat < 1:
					self.sel_dat =1
			self.showActiveDat()

	def down(self,num=None):
		if self.list_site==1:
			self["event_list"].selectNext()
		else:
			if self.sel_dat == self.monatstage:
				self.vor()
			else:
				self.sel_dat += 7
				if self.sel_dat > self.monatstage:
					self.sel_dat=self.monatstage
			self.showActiveDat()

	def showActiveDat(self):
		self.d2list=[]
		self.d3list = []
		msp_list=[]
		tp_txt=""
		for dat in self.d_list:
			d_test=0
			self.d3list = []
			if len(dat):
				for x in dat:
					if len(x):
						txt=str(x[0])
						if txt=='':
							txt=" "
						else:
							d_test=d_test+int(x[0])
						msp_color=None
						if conf["schicht_art"] and len(msp_liste):
							try:
								if txt !=" ":    
									tp=msp_liste[int(x[0])-1]
									msp_color=Farben().farb_re(tp[2])
								else:
									msp_color= Farben().farb_re(self.cal_background)
							except:
								pass 
						self.d3list.append(txt)
						self.d3list.append(Farben().farb_re(x[2]))
						self.d3list.append(Farben().farb_re(x[1]))
						if txt ==" ":
							self.d3list.append(Farben().farb_re(self.cal_background)) 
						elif int(self.sel_dat) == int(x[0]):
							self.d3list.append(0xffffff)
						else:
							self.d3list.append(0x000000)
							#self.d3list.append(Farben().farb_re(self.cal_background))
						if conf["schicht_art"] and msp_color: self.d3list.append(msp_color)    
				if d_test>0:
					self.d2list.append(tuple(self.d3list))

		self["calendar"].style = "default"
		if msp_color:
			self["calendar"].style = "with_schicht"
		self["calendar"].setList(self.d2list)
		tp_txt=""
		text=""
		datum=""
		location= ""
		kat1= None
		self.ed_list=[(_("Add new event"),(1,(self.sel_dat,self.monat,self.jahr),None,None))]
		if conf["schicht_art"] and len(msp_liste):
			le= msp_liste[int(self.sel_dat)-1]
			try:
				tp_txt1=str(le[1]).strip()
				tplus=""
				if len(le)>4 and le[4]:
					edt=le[4]
					zeit=(edt[2].hour,edt[2].minute)
					zeit2=(edt[3].hour,edt[3].minute)
					ed2=(le[3],edt[0],edt[1],edt[2],edt[3],edt[4],edt[5],self.jahr,edt[6],edt[7],edt[8],0,edt[9],edt[10],zeit, -1,edt[11],edt[12],zeit2,edt[13],0)
					self.ed_list.append((tp_txt,ed2))
					if zeit != (0,0) or zeit2 != (0,0):
						tplus=" "+str(zeit[0])+":"+str(zeit[1])+" - "+str(zeit2[0])+":"+str(zeit2[1])
				if len(str(tp_txt1)): 
					tp_txt=self.schicht_bez+": "+str(tp_txt1)+tplus
			except:
				pass
		date = datetime.date(self.jahr,self.monat,self.sel_dat)
		for x in self.eventliste3:
			try:
				if self.sel_dat>0 and datetime.date(x[0].year,x[0].month,x[0].day)== datetime.date(self.jahr,self.monat,self.sel_dat):
					kat=""
					datum=""
					zusatz=""
					zeit=""
					location=""
					ntext=""
					if len(x)>19:
						if len(str(x[19])):
							location= ", "+x[19]
					if len(x)>17 and x[17] != "ganztag" :
						zeit2=""
						zeit1=""
						zeit1='%0.2d:%0.2d ' %(x[3].hour,x[3].minute)
						zeit2='%0.2d:%0.2d ' %(x[4].hour,x[4].minute)
						if x[4].date()>x[3].date():
							if date==x[3].date():
								zeit2=" ..."
							elif date==x[4].date():
								zeit1="bis "
							else:
								zeit1="..."
								zeit2=""
						else:
							if zeit1 == zeit2:
								zeit2=""
							else:
								zeit1=zeit1+"- "
							zeit=" "+zeit1+zeit2
					try:
						anz_text=str(x[8]).replace("\n",", ").replace("\\"," ")
						if anz_text is None or not len(anz_text): 
							anz_text=str(x[1])
						elif x[1] not in anz_text: 
							anz_text = x[1]+", "+anz_text
						kat1=None
						if x[2]: kat1= str(x[2])
						if not kat1 or kat1 =="" or kat1 =="None":
							for tmp in categories1:
								if tmp.strip() in anz_text:
									kat1= tmp.strip()
									anz_text=anz_text.replace(tmp.strip()+":","")
						alter=""
						if kat1 and kat1 !="" and kat1 !="None":
							cat_ind=0
							for tmp in categories1:
								if kat1 and tmp.strip() in kat1:
									if z_liste[cat_ind]=="1":
										alter = " "+str(x[7] - int(x[3].year))
										break
								cat_ind+=1
							kat = " (" + _(kat1)+ alter+")"
					except:
						anz_text=str(x[1])
					ntext = " "+zeit+zusatz+anz_text+location+ kat+"\n"
					text = text+ntext        #+ kat
					self.ed_list.append((zusatz+x[1],x))
			except:
				continue

		day=date.weekday()
		day_name = days[day]
		datum=day_name+", " '%0.2d' %int(date.day)+". " + self.monatsname
		text = datum  +": "+tp_txt+"\n"+text.replace("dogage","") 
		self["descreption"].setText(str(text))

	def config_start(self):
		self.session.openWithCallback(self.config_back,PlanerFSConfiguration)

	def config_back(self,a=None,b=None,c=None):
		if c=="restart":
			self.close(self.session,True)

	def config_colors(self):
		self.session.openWithCallback(self.config_back,PFS_categorie_conf7)

	def new_termin(self,datum=None): 
		self.edit_index=None
		if self.kalnum==1:
			eigen_num=0
		else:
			eigen_num=3
		self.session.openWithCallback(self.editliste,PFS_edit_Termin,None,eigen_num,datum)

	def edit_termin(self): 
		if self.hlp:
			self.hlp=None
			self["help"].hide()
		else:
			if self.list_site==1: 
				if self["event_list"].getCurrent() is not None:
					index = self["event_list"].getCurrent()#[3]
					if index and len(index)>3: 
						try:
							index=index[3]
							if len(index) > 11 and str(index[12])=="br":
								text= _("Internal calculated holiday, import not possible")+"\n" 
								self.session.open(MessageBox, text, type = MessageBox.TYPE_INFO) 
							elif index[11]==0 or index[11]==3:
								if index[2] and index[2].upper()=="TIMER":
									self.edit_index=self.eigen_events.index(index[23])+1
								else:
									self.edit_index=self.eigen_events.index(index[24])+1
								self.session.openWithCallback(self.editliste,PFS_edit_Termin,index)
							else:
								self.import_termin = index
								text= _("Termin from downloaded file")+"\n"+index[12]+"\n" + _("external file can not be edited, Import this event?")   #+self["event_list"].l.getCurrentSelection()[0][12]+"\n"
								self.session.openWithCallback(self.edit_antwort, MessageBox, text, MessageBox.TYPE_YESNO)
						except Exception as e:
							self.session.openWithCallback(self.edit_antwort, MessageBox, str(e), MessageBox.TYPE_YESNO)

			else:
				self.session.openWithCallback(self.t_listCallback, ChoiceBox, title=_("Select for edit or new"), list=self.ed_list)

	def t_listCallback(self,choice):
		if choice is not None:
			if choice[1][0]==1:
				self.new_termin(choice[1][1])
			elif choice[1][11]==0 or choice[1][11]==3:
				self.edit_index=self.eigen_events.index(choice[1][24])+1
				self.session.openWithCallback(self.editliste,PFS_edit_Termin,choice[1])
			else:
				self.import_termin=choice[1]
				text= _("Termin from downloaded file")+"\n"+ _("external file can not be edited, Import this event?")
				self.session.openWithCallback(self.edit_antwort, MessageBox, text, MessageBox.TYPE_YESNO)

	def edit_antwort(self, answer=None):
		if answer and self.import_termin:
			g = self.import_termin
			if len(g)>20:
				if g[11]==0:
					text= _("Termin from downloaded file")+"\n"+self.import_termin[12]+"\n"+ _("Entry can only be copied from external to internal (*...)")
					self.session.open(MessageBox, text, type = MessageBox.TYPE_INFO)
				else:
					self.edit_index=None
					neulist= (g[1],g[2],g[3],g[4],g[5],g[6],g[8],None,None,None,None,g[18],g[17],g[19])
					self.editliste(neulist,None)
		self.import_termin=None

	def editliste(self, neueintrag,loesch=None):
		if loesch and str(loesch) == "aktloesch":
			self.delete_termin()
		elif neueintrag:
			eventliste=self.eigen_events
			try:
				if self.edit_index:
					del eventliste[self.edit_index-1]
			except:
				pass
			if loesch is None: eventliste.append(neueintrag)
			events=[]
			ev_start="BEGIN:VCALENDAR\nMETHOD:PUBLISH\nPRODID: -EnigmaII-Plugin / PlanerFS "+my_version+"\nVERSION:2.0"
			events.append(ev_start)
			if self.kalnum==1:
				fname="PlanerFS.ics"
			else:
				fname="PlanerFS2.ics"
			for x in eventliste:
				if x[9] is None or fname in str(x[9]):
					anzeige=""
					comment=""
					location=""
					on="\nBEGIN:VEVENT\n"
					off="END:VEVENT"
					if x[12]!="Yes" and x[12]!="ganztag":
						start_dat = strftime("DTSTART;TZID=Europe/Berlin:%Y%m%dT%H%M%S\n",strptime(str(x[2]), "%Y-%m-%d %H:%M:%S"))
						end_dat = strftime("DTEND;TZID=Europe/Berlin:%Y%m%dT%H%M%S\n",strptime(str(x[3]), "%Y-%m-%d %H:%M:%S"))
					else:
						start_dat = strftime("DTSTART;VALUE=DATE:%Y%m%d\n",strptime(str(x[2]), "%Y-%m-%d %H:%M:%S"))
						ed2=x[3]
						if x[2] != x[3]:ed2 = x[3] + datetime.timedelta(1)
						end_dat = strftime("DTEND;VALUE=DATE:%Y%m%d\n",strptime(str(ed2), "%Y-%m-%d %H:%M:%S"))                    
					self.altdatum = x[3]
					summary="SUMMARY:"+x[0]+"\n"
					desc=x[6]
					if x[6] is None or x[6]=="" or x[6]=="None": desc=x[0]
					desc= "DESCRIPTION:"+desc+"\n"
					if len(str(x[13].strip())):location= "LOCATION:"+x[13].strip()+"\n"
					if str(x[4]) == "no_startscreen" or len(x)>16 and str(x[16])=="1":
						location= location+"ACTION:no_startscreen\n"
					if x[1]=="TIMER":
						anzeige="BEGIN:VALARM\nACTION:"+str(x[4]).strip() +"\nTRIGGER;VALUE=DURATION:-PT1M\n"+desc+"END:VALARM\n"
					elif x[4]=="DISPLAY":
						anzeige="BEGIN:VALARM\nACTION:DISPLAY\nTRIGGER;VALUE=DURATION:-P1D\n"+desc+"END:VALARM\n"
					cat=""
					if x[1]: cat="CATEGORIES:"+ x[1]+"\n"
					rule=""
					if x[5] and x[5][0] is not None: 
						self.altdatum = datetime.datetime.today()+datetime.timedelta(1)
						rule="RRULE:FREQ="+x[5][0]
						if x[5][1] is not None: rule=rule+";INTERVAL="+str(x[5][1])
						if x[5][2] is not None: rule=rule+";BYMONTH="+', '.join([str(t) for t in x[5][2]])
						if x[5][7] is not None: rule=rule+";BYDAY="+', '.join([str(t) for t in x[5][7]])
						if x[5][3] is not None: rule=rule+";BYMONTHDAY="+', '.join([str(t) for t in x[5][3]])
						if x[5][4] is not None: 
							self.altdatum = x[5][4]
							untile= strftime(";UNTIL=%Y%m%dT%H%M%S",strptime(str(x[5][4]), "%Y-%m-%d %H:%M:%S"))
							rule=rule+untile
						if x[5][6] is not None: rule=rule+";BYHOUR="+str(x[5][6])
						if x[5][5] is not None: rule=rule+";BYMINUTE="+str(x[5][5])
						if x[5][8] is not None: rule=rule+";BYYEARDAY="+str(x[5][8])
						if x[5][9] is not None: rule=rule+";BYWEEKNO="+str(x[5][9])
						if x[5][10] is not None: rule=rule+";BYWEEKST="+str(x[5][10])
						if x[5][11] is not None: rule=rule+";COUNT="+str(x[5][11])
						rule=rule+"\n"
					if x[10] and x[10] != None:comment="COMMENT:"+x[10]+"\n"
					trigger=""
					#if str(x[14]) == "0" or str(x[14]) == "1" or str(x[14]) == "None":x[14]=None 
					if len(x)>14 and x[14] and str(x[14]) != "0" and str(x[14]) != "1":trigger="BEGIN:VALARM\nACTION:DISPLAY\n"+str(x[14]).strip()+"\nEND:VALARM\n"
					detailliste=on+start_dat+end_dat+summary+cat+rule+desc+anzeige+comment+location+trigger+off
					if conf["altloesch_on"]=="No":
						events.append(str(detailliste))
					else:
						if self.altdatum >= self.altdat:
							events.append(str(detailliste))
						else:
							continue

			events.append("\nEND:VCALENDAR")
			self.edit_index=None
			f2=open(dat_dir+fname,"w")
			f2.writelines(events)
			f2.close()
			self.einlesen()
			from .plugin import Termin_Timer
			aktual=Termin_Timer().aktual()
		else:
			self.liste_anzeigen()

	def delete_termin(self): 
		k=1
		t=""
		rule=None
		try:
			if self.edit_index is None: 
				self.edit_index=self.eigen_events.index(self["event_list"].getCurrent()[3][24])+1
			dat=self.eigen_events[self.edit_index-1]
			t= dat[0]
			rule=dat[5]
		except Exception as e:
			k=None
		if k:
			text1="\n"+t+"\n\n"
			if rule:
				self.session.openWithCallback(self.delete_termin_ok,MessageBox,_(text1+_("Caution, this is a recurring appointment! Delete recurring appointment?")) ,MessageBox.TYPE_YESNO)
			else:
				self.session.openWithCallback(self.delete_termin_ok,MessageBox,_(text1+_("Do you really want to delete this entry?")) ,MessageBox.TYPE_YESNO)

	def delete_termin_ok(self,answer=None):
		if answer:
			self.editliste(1,1)

	def exit(self):
		if self.hlp:
			self.hlp=None
			self["help"].hide()
		else:
			self.close(None)

class PanerFS_menu7(Screen):
	if screen_size=="SD":
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFSmenulist.xml"
	elif screen_size=="fHD":
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFSmenulist.xml"
	else:
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFSmenulist.xml"

	tmpskin = open(skin)
	skin = tmpskin.read()
	tmpskin.close()
	def __init__(self, session, extern):
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.session = session
		lista = []
		self["menulist"]=List([])
		nr=1
		lista.append(("1"," "+_("Insert new event / timer"), "new_termin"))
		if extern==0 or extern==3:
			lista.append(('2'," "+_("edit selected  entry"), "edit_termin")) 
			lista.append(('3'," "+_("Delete selected  entry"), "delete_termin"))
			nr=3
		elif extern==2:
			lista.append(('2'," "+_("Import selected  entry"), "import_termin"))
			nr=2
		#lista.append((" ","", "nix"))
		lista.append((str(nr+1)," "+"PlanerFS: "+_("parameters setting"), "config_start"))
		lista.append((str(nr+2)," "+"PlanerFS: "+_("Color an category setting"), "config_colors"))
		lista.append((str(nr+3)," "+_("Files Handling"), "fileHandling"))
		lista.append((str(nr+4)," "+_("Edit online calendar list"), "Online_cal"))
		if (conf["adr_on"]):
			lista.append((str(nr+5)," "+_("Open adress book"), "Adress_cards"))
			nr=nr+1
		if conf["schicht_art"]:
			lista.append((str(nr+5)," "+_("Setting shifts"), "Setting_shifts"))
			lista.append((str(nr+6)," "+_("Show/Hide Shift dates"), "Shift dates"))
			nr=nr+2
		if os.path.exists('/tmp/PlanerFS-Errors.txt') and os.path.getsize("/tmp/PlanerFS-Errors.txt")>60:
			lista.append((" "," "+_("Show errors"), "show_errors"))
		lista.append((" "," "+_("About the plugin"), "about"))
		if modul==0:
			lista.append((" ","", "nix"))
			lista.append((" "," "+_("info, no ical-module"), "info_ical"))

		self.setTitle("PlanerFS: "+_("Menu"))
		self["menulist"].setList(lista)

		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions","DirectionActions"],
		{
			"ok": self.run,
			"cancel": self.exit,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
		}, -1)

	def keyNumberGlobal(self, number):
		self["menulist"].setIndex(number-1)
		self.run()


	def run(self):
		returnValue = self["menulist"].getCurrent()[2]
		if returnValue != "nix":
			self.close(returnValue)

	def exit(self):
		returnValue=None
		self.close(returnValue)