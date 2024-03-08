# -*- coding: utf-8  -*-
from . import pyvers, my_version, _

from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.HelpMenu import HelpableScreen
from Screens.InfoBarGenerics import InfoBarNotifications
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Input import Input
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from enigma import getDesktop
from enigma import ePicLoad,eTimer
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigInteger, \
	ConfigYesNo, ConfigText, ConfigClock, ConfigSelection, ConfigNumber, ConfigSubList, ConfigSequence, \
	config, NoSave

from skin import parseColor, parseFont
import os.path
import time
import datetime
import re, io
import codecs
import base64
if pyvers==3:
	from base64 import decodebytes, encodebytes 
from time import localtime, mktime,strftime

from .routines_vc import Cards_parse

try:
	from Plugins.Extensions.FritzCall.plugin import FritzCallFBF
	fbf = FritzCallFBF
except ImportError:
    fbf = None
DWide = getDesktop(0).size().width()

cardfile = "/etc/ConfFS/PlanerFS.vcf"

color_list=[]
if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
	configparser = ConfigParser()
	configparser.read("/etc/ConfFS/PlanerFS.conf")
	if configparser.has_option("settings","cat_color_list"): 
		color_list=configparser.get("settings","cat_color_list")
		color_list= color_list.split(",")

if len(color_list)<18:
	color_list=("#00008B","#D2691E","#006400","#696969","#FFD700","#000000","#B22222","#8B8878","#CD0000","#00868B","#f0f8ff","#ff4500","#20343c4f","#deb887","#228B22","#5F9EA0","#DC143C","#F0F8FF","#EEC900")
color_days = color_list[10]
cal_background=color_list[12]


size_w = getDesktop(0).size().width()
size_h = getDesktop(0).size().height()

def det_liste(glist=None):
		cards2=[]
		for x in glist:
			detailliste=""
			on="BEGIN:VCARD\n"
			off="END:VCARD\n"
			name=x[2][0]+":"+x[2][1].encode("utf-8").decode('utf-8')+"\n"
			anzeige_name=x[1][0]+":"+x[1][1]+"\n"
			adr1=""
			if len(x[3][1].replace(";",""))>1: adr1= x[3][0]+":"+x[3][1]+"\n"
			adr2=""
			if len(x[4][1].replace(";",""))>1: adr2= x[4][0]+":"+x[4][1]+"\n"
			mail=""
			if len(x[5][1])>0: mail=x[5][0]+":"+x[5][1]+"\n"
			geburtstag=""
			if  x[6][1] !="0-1-1" and len(x[6][1])>0:geburtstag = x[6][0]+":"+x[6][1]+"\n"
			if len(x[11]): notiz=x[11][0]+":"+ x[11][1]
			tel_x=""
			for x_tel in x[7]:
				if len(x_tel[2]):  
					if "WORK" in x_tel[0]  or "WORK" in str(x_tel[1]).upper():
						bez1b="TEL;WORK;VOICE:"
					elif "MOBIL" in x_tel[0] or "CELL" in str(x_tel[1]).upper():
						bez1b="TEL;CELL;VOICE:"
					elif "HOME" in x_tel[0] or "HOME" in str(x_tel[1]).upper():
						bez1b="TEL;HOME;VOICE:"
					else:
						bez1b="TEL;:"
					tel_x=tel_x+bez1b+str(x_tel[2])+"\n"

			zus_list=""
			if len(x[8])>0:
				for x4 in x[8]:
					if len(x4)>0:
						zus_list=zus_list+x4#+"\n"
			try:
				if x[10][1] != "": 
					pic=x[10][0]+":\n"
					if pyvers==2:
						pic2=base64.decodestring(x[10][1])
						pic3=base64.encodestring(pic2)
						pic4=pic3.split("\n")
					else:
						pic4=encodebytes(decodebytes(x[10][1].encode())).decode().split("\n")
					for ze in pic4:
						pic = "%s %s\n" % (pic, ze)
					zus_list=zus_list+pic
			except:
				pass
			detailliste=on+anzeige_name+name+adr1+adr2+mail+geburtstag+tel_x+zus_list+off
			cards2.append(str(detailliste))
		return cards2


class PFS_show_card7(Screen, InfoBarNotifications):
	ALLOW_SUSPEND = True
	if size_w < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFScard.xml"
	elif size_w > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFScard.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFScard.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session,name=None,geb=None,index=None):
		self.name=name
		self.geb=None
		self.index=index
		Screen.__init__(self, session)
		self.skinName = "show_card7"
		InfoBarNotifications.__init__(self)
		self["tel_listlabel"]=List([])
		self["tel_listlabel"].onSelectionChanged.append(self.changed)
		self["key_green"] = Label(_("New Card"))
		self["key_red"] = Label(_("Close"))
		self["key_yellow"] = Label(_("Edit"))
		self["key_blue"] = Label("")
		self["adr"] = Label("")
		self["mail"] = Label("")
		self["geb"] = Label("")
		self["bild"] = Pixmap()
		self.pic_file=None
		self["adr_background"] = Label()
		self["adr2_background"] = Label()
		self["Actions"] = ActionMap(["OkCancelActions","DirectionActions", "ColorActions"],
		{
			"green": self.new_card,
			"blue": self.call,
			"red": self.close,
			"yellow": self.edit,
			"cancel": self.cancel,
			"ok": self.cancel,
		}, -2)
		self.picload = ePicLoad()
		self.ds=[]
		dummi=eTimer()
		if hasattr(dummi, 'callback'):
			self.picload.PictureData.get().append(self.setPictureCB)
		else:
			self.picload_conn = self.picload.PictureData.connect(self.setPictureCB)
		self.onLayoutFinish.append(self.run)
		dummi=None

	def run(self):
		self.read_new(self.name,self.geb,self.index)

	def tel_liste_anzeigen(self):
		self["adr"].setText(str(self.adr))
		self["mail"].setText(str(self.mail))
		self["geb"].setText(str(self.geb4))
		self.tel1=[]
		self.setTitle("PlanerFS "+_("business card")+" - "+self.name)
		if len(self.ds[10]):
			if self.ds[10][1] and self.ds[10][1] != "":
				self.pic_file="/tmp/plfs_pic."+self.ds[10][2]
				f=open(self.pic_file,"wb")
				pic= base64.b64decode(self.ds[10][1])#base64.decodestring(self.ds[10][1])
				f.write(pic)
				f.close()
				self.setPicture(self.pic_file)
		if len(self.tel)>0:   
			for x in self.tel:
				if len(x[2].replace(' ',''))>0:
					self.tel1.append((str(x[0]),str(x[2]),x[0],x[2]))
			if fbf == None:
				self["tel_listlabel"].style = "not selected"
			else:
				self["tel_listlabel"].style = "default"
		self["tel_listlabel"].setList(self.tel1)

	def edit(self):
		if len(self.ds):
			self.session.openWithCallback(self.read_new,PFS_edit_cards,self.ds,self.index,self.new_geb)

	def new_card(self):
		self.session.openWithCallback(self.read_new,PFS_edit_cards)

	def read_new(self,name=None,geb=None,index=None):
		if name or index:
			self.name=name
			self.new_geb=None
			self.index=index
			self.cards_liste=PFS_read_vcards().cards1
			self.tel=[]
			self.ds=[]
			new=0
			self.adr=""
			self.name=""
			self.mail="Mail:\n"
			self.geb4=_("Birthday")+":\n"
			if self.name==None and self.index==None:
				pass
			elif self.index != None:
				for x in self.cards_liste:
					if x[0]==self.index:
						self.ds= x
			elif self.name:
				if geb:
					geb2=geb
				else:
					geb2="0-1-1"
				self.ds=[None,["N",""],["FN",self.name],["ADR;HOME",";;;;;;"],["ADR;WORK",";;;;;;"],["EMAIL;PREF;INTERNET"," "],["BDAY",geb2],[],(),"",("",""),("","")]
				if len(self.cards_liste)>0:
					for x in self.cards_liste:
						if x[2][1].upper() == self.name.upper():
							self.ds=x
							if self.ds[6][1]=="0-1-1":
								self.new_geb=geb
							break
						else:
							pass

			if len(self.ds)>0:
				if self.ds[3] and self.ds[3][1] and len(self.ds[3][1])>7:
					adresse=self.ds[3][1].strip('\r\n')
				elif self.ds[4] and self.ds[4][1] and len(self.ds[4][1])>7:
					adresse=self.ds[4][1].strip('\r\n')
				else:
					adresse=_("No entry found in business cards")
				adress=adresse.split(";") 
				for a in adress:
					a2=a.strip('\r\n')
					if len(a2)>0:
						self.adr= self.adr+a2+"\n"
				if self.ds[5] and self.ds[5][1]:
					self.mail="Mail:\n"+self.ds[5][1]
				self.name=self.ds[2][1]

				if self.new_geb:
					geb2=self.new_geb.split("-")
					self.geb4=_("Birthday")+":\n" + '%0.2d.%0.2d.%0.4d' %(int(geb2[2]),int(geb2[1]),int(geb2[0]))

				elif self.ds[6] and self.ds[6][1] !="0-1-1" and len(self.ds[6][1])>0:
					geb2=self.ds[6][1].split("-")
					self.geb4=_("Birthday")+":\n" + '%0.2d.%0.2d.%0.4d' %(int(geb2[2]),int(geb2[1]),int(geb2[0]))

				if self.ds[1] and self.ds[1][1]:
					anzeigename=self.ds[1][1]

				if self.ds[7]:
					self.tel=self.ds[7]
			else:
				self.ds=[None,["N",""],["FN",""],["ADR;HOME",";;;;;;"],["ADR;WORK",";;;;;;"],["EMAIL;PREF;INTERNET"," "],["BDAY","0-1-1"],[],(),"",("","","")]
			self.tel_liste_anzeigen()

	def call(self):
		if fbf and len(str(self["tel_listlabel"].getCurrent()[1]))>1:
			p_num=str(self["tel_listlabel"].getCurrent()[1])
			p_num=p_num.replace(" ","")
			fbf().dial(p_num)
		else:
			self.session.open(MessageBox, "no FritzCall installed", type = MessageBox.TYPE_INFO)


	def changed(self):
		self["key_blue"].setText(" ")
		if fbf and self["tel_listlabel"].getCurrent() is not None:
			if self["tel_listlabel"].getCurrent()[1]:
				self["key_blue"].setText(_("Call Number"))
				self.akt_tel_nr=str(self["tel_listlabel"].getCurrent()[1])

	def cancel(self):
		if self.pic_file:
			os.remove(self.pic_file)
		self.close()

	def setPicture(self, string):
		sc = AVSwitch().getFramebufferScale()
		self.picload.setPara([self["bild"].instance.size().width(), self["bild"].instance.size().height(), 1, 1, 0, 1, 'transparent'])
		self.picload.startDecode(string)

	def setPictureCB(self, picInfo = None):
		ptr = self.picload.getData()
		if ptr is not None:
			self["bild"].instance.setPixmap(ptr.__deref__())

class PFS_edit_cards(ConfigListScreen,Screen, InfoBarNotifications):
	ALLOW_SUSPEND = True
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFSconf.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFSconf.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFSconf.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session,ds=[],index=None,new_geb=None):
		self.cards_liste=PFS_read_vcards().cards1
		self.index=index
		self.ds=ds
		if self.index:
			for x in self.cards_liste:
				if x[0]==self.index:
					self.ds= x
				else:
					self.ds=ds

		self.zus=[]
		if len(self.ds)>7:
			#for 1 to 
			self.zus=self.ds[8]
		if len(self.ds)<1:
			self.ds=[None,["N",""],["FN",""],["ADR;HOME",";;;;;;"],["ADR;WORK",";;;;;;"],["EMAIL;PREF;INTERNET",""],["BDAY","0-1-1"],[],(),"",("",""),("","")]
		self.name=NoSave(ConfigText(default = "", fixed_size = False))
		self.name.value=self.ds[2][1].encode("utf-8")
		self.anzeigename=NoSave(ConfigText(default = self.ds[1][1], fixed_size = False))
		self.adress_home=self.ds[3][1].split(";")
		if len (self.adress_home)<7:
			self.adress_home.extend(('','','','','',''))
		self.adress_work=self.ds[4][1].split(";")
		if len (self.adress_work)<7:
			self.adress_work.extend(('','','','','',''))
		if new_geb:
			geb=new_geb.split("-")
		else:
			geb=self.ds[6][1].split("-")
		tel_ges1=["","","","",""]
		if len(self.ds[7]):
			for x in self.ds[7]:
				if _("WORK") in x[0]: 
					tel_ges1[0]=x[2]
				elif _("HOME") in x[0]:
					tel_ges1[1]=x[2]   
				elif _("MOBIL") in x[0]:
					tel_ges1[2]=x[2] 
		self.strasse=NoSave(ConfigText(default = self.adress_home[2], fixed_size = False))
		self.ort=NoSave(ConfigText(default = self.adress_home[3], fixed_size = False))
		self.plz=NoSave(ConfigText(default = str(self.adress_home[5]), fixed_size = False))
		self.land= NoSave(ConfigText(default=self.adress_home[6], fixed_size = False))
		self.strasse_w=NoSave(ConfigText(default = self.adress_work[2], fixed_size = False))
		self.ort_w=NoSave(ConfigText(default = self.adress_work[3], fixed_size = False))
		self.plz_w=NoSave(ConfigText(default = str(self.adress_work[5]), fixed_size = False))
		self.land_w= NoSave(ConfigText(default=self.adress_work[6], fixed_size = False))
		self.mail=NoSave(ConfigText(default = self.ds[5][1], fixed_size = False))
		dat_limits = [(1,31),(1,12),(0,3000)]
		self.geburtstag = NoSave(ConfigSequence(seperator = ".",limits=dat_limits,default =[int(geb[2]),int(geb[1]),int(geb[0])]))
		self.tel_work = NoSave(ConfigText(default=tel_ges1[0], fixed_size = False))
		self.tel_home = NoSave(ConfigText(default=tel_ges1[1], fixed_size = False))
		self.tel_mobil = NoSave(ConfigText(default=tel_ges1[2], fixed_size = False))
		self.tel_4 = NoSave(ConfigText(default=tel_ges1[3], fixed_size = False))
		self.tel_5 = NoSave(ConfigText(default=tel_ges1[4], fixed_size = False))

		Screen.__init__(self, session)
		self.skinName="PFSconf"
		InfoBarNotifications.__init__(self)
		self.extended=None
		self.refresh()

		ConfigListScreen.__init__(self, self.list)
		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("extended"))
		self["key_blue"] = Label("")
		self["help"] = Label(_("Press 'OK' for Virtual Keyboard"))
		self["setupActions"] = ActionMap(["SetupActions","DirectionActions", "ColorActions"],
		{
			"green": self.save,
			"blue": self.call,
			"red": self.cancel1,
			"yellow": self.set_extend,
			"cancel": self.cancel1,
			"down": self.downPressed,
			"up": self.upPressed,
			"ok": self.ok,
		}, -2)
		self.setTitle(_("PlanerFS: ")+_("vCard - Edit"))
		self.reloadList()


	def call(self):
		if fbf and len(str(self["config"].getCurrent()[1].getText()))>1:
			p_num=str(self["config"].getCurrent()[1].getText())
			fbf().dial(p_num)

	def refresh(self):
		list = []
		list.extend((
			getConfigListEntry(_("Name"), self.name),
			getConfigListEntry(_("Designation"), self.anzeigename),
			getConfigListEntry(_("Street"), self.strasse),
			getConfigListEntry(_("City"), self.ort),
			getConfigListEntry(_("zip code"), self.plz),
			getConfigListEntry(_("land"), self.land),
			getConfigListEntry(_("Email"), self.mail),
			getConfigListEntry(_("Birthday"), self.geburtstag),
			getConfigListEntry(_("Tel. "+_("HOME")), self.tel_home),
			getConfigListEntry(_("Tel. "+_("MOBIL")), self.tel_mobil),
			getConfigListEntry(_("Tel. "+_("WORK")), self.tel_work),
			))

		if self.extended:
			list.extend((
				getConfigListEntry(_("Tel.4 "), self.tel_4),
				getConfigListEntry(_("Tel.5 "), self.tel_5),
				getConfigListEntry(_("WORK"),),
				getConfigListEntry(_("Street")+" ("+_("WORK")+")", self.strasse_w),
				getConfigListEntry(_("City")+" ("+_("WORK")+")", self.ort_w),
				getConfigListEntry(_("zip code")+" ("+_("WORK")+")", self.plz_w),
				getConfigListEntry(_("land")+" ("+_("WORK")+")", self.land_w),
				))

		self.list = list

	def set_extend(self):
		if self.extended==1:
			self.extended=None 
		else:
			self.extended=1
		self.reloadList()   

	def reloadList(self):
		self.refresh()
		self["config"].setList(self.list)

	def downPressed(self):
		l=len(self.list)
		idx = self["config"].getCurrentIndex()
		idx=idx+1
		if idx < l:
			self.reloadList()
			self["config"].setCurrentIndex(idx)
			self.help()

	def upPressed(self):
		idx = self["config"].getCurrentIndex()
		idx=idx-1
		self.reloadList()
		self["config"].setCurrentIndex(idx)
		self.help()


	def help(self):
		self["key_blue"].setText("")
		helptxt=""
		cur = self["config"].getCurrent()
		cur = cur and cur[1]
		if cur == self.tel_home or cur==self.tel_mobil or cur==self.tel_work or cur==self.tel_4 or cur==self.tel_5:
			if fbf and len(str(self["config"].getCurrent()[1].getText()))>1:
				self["key_blue"].setText(_("Call Number"))
				helptxt=_("Edit Call-Number")+"\n"+_("or\n call the Number with blue Key")
			else:
				helptxt=_("Edit Call-Number")
		elif cur == self.name or cur==self.strasse or cur==self.ort or cur==self.mail or cur==self.anzeigename: 
			helptxt=_("Press 'OK' for Virtual Keyboard")
		else:
			helptxt=_("No help text available")
		self["help"].setText(helptxt)


	def texteingabeFinished(self, ret):
		if ret is not None:
			self.cur.value = ret
			self.refresh()

	def ok(self):
		self.cur = self["config"].getCurrent()
		self.cur = self.cur and self.cur[1]
		if self.cur == self.name or self.cur==self.strasse or self.cur==self.ort or self.cur==self.mail or self.cur==self.anzeigename or self.cur==self.plz_w:
			self.session.openWithCallback(self.texteingabeFinished,VirtualKeyBoard, title=_("vCard- edit Text"), text=self.cur.value)
		elif self.cur == self.tel_home or self.cur==self.tel_mobil or self.cur==self.tel_work or self.cur==self.tel_4 or self.cur==self.tel_5:
			self.session.openWithCallback(self.texteingabeFinished,InputBox, title=_("vCard- edit Number"), text=self.cur.value,maxSize = False,type=Input.NUMBER)
		else:
			pass

	def delete1(self):
		self.session.openWithCallback(self.delete2, MessageBox, _("Selected card delete?"), MessageBox.TYPE_YESNO)

	def delete2(self, answer=None):
		if answer:
			self.save2()

	def save(self):
		self.save2("neu")

	def save2(self,neueintrag=None):
		if self.ds and len(self.ds):
			try:
				ind= self.cards_liste.index(self.ds)
				del self.cards_liste[ind]
			except:
				pass
		else:
			self.index=None
		if neueintrag=="neu":
			if not len(self.anzeigename.value):
				self.anzeigename.value=self.name.value
			adr_ges= (self.ds[3][0],self.adress_home[0]+";"+self.adress_home[1]+";"+self.strasse.value+";"+self.ort.value+";"+self.adress_home[4]+";"+self.plz.value+";"+str(self.land.value))
			adr_w_ges= (self.ds[4][0],self.adress_work[0]+";"+self.adress_work[1]+";"+self.strasse_w.value+";"+self.ort_w.value+";"+self.adress_work[4]+";"+self.plz_w.value+";"+str(self.land_w.value))
			self.tel_ges= (("HOME","",self.tel_home.value),("MOBIL","",self.tel_mobil.value),("WORK","",self.tel_work.value),("TEL;: ","",self.tel_4.value),("TEL;: ","",self.tel_5.value))
			geburtstag = (self.ds[6][0],str(self.geburtstag.value[2])+"-"+str(self.geburtstag.value[1])+"-"+str(self.geburtstag.value[0]))
			neueintrag=(None,(self.ds[1][0],self.anzeigename.value),(self.ds[2][0],self.name.value),adr_ges,adr_w_ges,(self.ds[5][0],self.mail.value),geburtstag,self.tel_ges,self.ds[8],self.ds[9],self.ds[10],self.ds[11])
			self.cards_liste.append(neueintrag)
		cards3=det_liste(self.cards_liste)
		if pyvers==3:
			with io.open(cardfile, mode='w', encoding='cp1252') as fd:
				fd.writelines(cards3)
		else:
			f=open(cardfile, "wb")
			for x in cards3:
				f.write(x.strip('\r\n').encode('cp1252')+"\n")
			#f.writelines(cards3)
			f.close()
		self.close(self.name.value,None,self.index)

	def cancel1(self):
		self.close(self.name.value,None,self.index)

class PFS_read_vcards:
	def __init__(self):
		dataLines = []
		self.cards1 = []
		if os.path.isfile(cardfile): 
			with io.open(cardfile, "r", encoding="cp1252") as f:
				dataLines=f.readlines()
		if dataLines:
			mask = {}
			mask['BEGIN'] = re.compile("^BEGIN:VCARD")
			mask['END'] = re.compile("^END:VCARD")
			inCard= False
			index=0
			for line in dataLines: 
				if mask['BEGIN'].match(line):
					cardLines = []
					inCard = True
				elif mask['END'].match(line) and inCard:
					parse1 = Cards_parse().parseCards(cardLines,index)
					self.cards1.append(parse1)
					inCard = False
					index+=1
				elif inCard:
					cardLines.append(line)
		self.cards1.sort(key=lambda x:x[9])

class PFS_show_card_List7(Screen, HelpableScreen, InfoBarNotifications):
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFScard_list.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFScard_list.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFScard_list.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session,cal_on=None):
		self.cal_on=cal_on
		self.cards_liste=PFS_read_vcards().cards1
		#self.cards_liste.sort(key=lambda x:x[1][1])
		Screen.__init__(self, session)
		self.skinName="show_card_List7"
		HelpableScreen.__init__(self)
		InfoBarNotifications.__init__(self)
		self.bs_list=(("nix",_("All")),("a","A","\xc3\xa4","\xc3\x84"),("b","B"),("c","C"),("d","D"),("e","E"),("f","F"),("g","G"),("h","H"),("i","I"),("j","J"),("k","K"),("l","L"),("m","M"),("n","N"),("o","O","\xc3\xb6","\xc3\x96"),("p","P"),("q","Q"),("r","R"),("s","S"),("t","T"),("u","U","\xc3\xbc","\xc3\x9c"),("v","V"),("w","W"),("x","X"),("y","Y"),("z","Z"))
		self.bs_index=0
		self.filter_on=None
		self["name_listlabel"] = List([]) 
		self["filter_background"] = Label()
		self["key_green"] = Label(_("New Card"))
		self["key_red"] = Label(_("Delete"))
		self["key_yellow"] = Label(_("Edit"))
		self["key_blue"] = Label(_("Calendar"))
		for x in range(27):
			self["d" + str(x)] = Label()
			self["d" + str(x)].setText(self.bs_list[x][1])
		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"red": (self.delete, _("Delete  buisness card of selected Name")),
			"green": (self.new, _("Make new buisness card")),
			"yellow": (self.edit, _("Edit data of selected name")),
			"blue": (self.blue,  _("Open Calendar")),
			}, -2)
		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
		{
			"cancel": (self.close, _("Close adress book")),
			"ok": (self.show_card, _("Show  buisness card of selected Name")),
			}, -2)
		self["EPGSelectActions"] = HelpableActionMap(self, "EPGSelectActions",
		{
			"prevBouquet": (self.filter_back, _("Filter - Letter up")),
			"nextBouquet": (self.filter_next, _("Filter - Letter down"))
			}, -2)
		self.setTitle("PlanerFS "+_("business card")+" - Liste")
		self.onLayoutFinish.append(self.name_liste_anzeigen)

	def delete(self):
		self.session.openWithCallback(self.delete2, MessageBox, _("Selected card delete?"), MessageBox.TYPE_YESNO)

	def new(self):
		self.session.openWithCallback(self.read,PFS_edit_cards) 

	def show_card(self):
		if self["name_listlabel"].getCurrent():   
			l1=self["name_listlabel"].getCurrent()
			self.session.openWithCallback(self.read,PFS_show_card7,l1[0],None,l1[1][0])

	def edit(self):
		if self["name_listlabel"].getCurrent():   
			l1=self["name_listlabel"].getCurrent()
			self.session.openWithCallback(self.read,PFS_edit_cards,l1[1],l1[1][0],None)
		else:
			self.new()

	def read(self, *args, **kwargs):
		self.cards_liste=PFS_read_vcards().cards1
		self.name_liste_anzeigen()

	def filter_back(self):
		self["d" + str(self.bs_index)].instance.setBackgroundColor(parseColor(cal_background))
		self["d" + str(self.bs_index)].instance.setForegroundColor(parseColor(color_days))
		if self.bs_index>0:
			self.bs_index-=1
		else:
			self.bs_index=26
		bs=self.bs_list[self.bs_index]
		self["d" + str(self.bs_index)].instance.setBackgroundColor(parseColor("#C8EAFF"))
		self["d" + str(self.bs_index)].instance.setForegroundColor(parseColor("#000000"))
		self.filter2(bs)

	def filter_next(self):
		self["d" + str(self.bs_index)].instance.setBackgroundColor(parseColor(cal_background))
		self["d" + str(self.bs_index)].instance.setForegroundColor(parseColor(color_days))
		if self.bs_index<26:
			self.bs_index+=1
		else:
			self.bs_index=0
		bs=self.bs_list[self.bs_index]
		self["d" + str(self.bs_index)].instance.setBackgroundColor(parseColor("#C8EAFF"))
		self["d" + str(self.bs_index)].instance.setForegroundColor(parseColor("#000000"))
		self.filter2(bs)

	def blue(self,args=None):
		self.close(self.session,"planer")

	def filter2(self,buchstabe=None):
		if buchstabe:
			if buchstabe==('nix', _("All")):
				self.name_liste_anzeigen()
			else:
				self.filter_on=1
				filtered = [x for x in self.cards_liste if x[1][1].startswith(buchstabe)]
				n_list=[]
				for x in filtered:
					res = [ x ]
					if len(x[1][1].strip()):
						text1= str(x[1][1])
					else:
						text1= str(x[2][1])
					n_list.append((text1,x))
				self["name_listlabel"].setList(n_list)

	def name_liste_anzeigen(self,args=None):
		self["filter_background"].instance.setBackgroundColor(parseColor(cal_background))
		self["d0"].instance.setBackgroundColor(parseColor("#C8EAFF"))
		self["d0"].instance.setForegroundColor(parseColor("#000000"))
		for x in range(1,27):
			self["d" + str(x)].instance.setBackgroundColor(parseColor(cal_background))
			self["d" + str(x)].instance.setForegroundColor(parseColor(color_days))
		n_list=[]
		for x in self.cards_liste:
			res = [ x ]
			if len(x[1][1].strip()):
				text1= str(x[1][1])
			else:
				text1= str(x[2][1])
			n_list.append((text1,x))
		self["name_listlabel"].setList(n_list)

	def cancel(self):
		self.close(None)

	def delete2(self, answer=None):
		if answer:
			try:
				ind=self.cards_liste.index(self["name_listlabel"].getCurrent()[1])
				del self.cards_liste[ind]
				cards3=det_liste(self.cards_liste)
				f2=open(cardfile,"w")
				f2.writelines(cards3)
				f2.close()
				self.read()
			except:
				self.session.open(MessageBox, _("could not be deleted"), MessageBox.TYPE_ERROR)