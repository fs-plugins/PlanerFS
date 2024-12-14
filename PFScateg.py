from . import DWide, _

from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from skin import parseColor
from Components.Label import Label
from Components.Sources.List import List
from Components.Input import Input
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
from Components.ActionMap import ActionMap,HelpableActionMap
import os.path

pfscolor_list=("#006400","#BDB76B","#556B2F","#CAFF70","#BCEE68","#A2CD5A","#6E8B3D","#8FBC8F","#C1FFC1",
"#B4EEB4","#9BCD9B","#698B69","#228B22","#ADFF2F","#7CFC00","#90EE90","#20B2AA","#32CD32","#3CB371","#00FA9A","#F5FFFA","#6B8E23","#C0FF3E","#B3EE3A","#9ACD32",
"#698B22","#98FB98","#9AFF9A","#7CCD7C","#548B54","#2E8B57","#54FF9F","#4EEE94","#43CD80","#00FF7F","#00EE76","#00CD66","#008B45","#7FFF00","#76EE00","#66CD00",
"#458B00","#00FF00","#00EE00","#00CD00","#008B00","#F0E68C","#FFF68F","#EEE685","#CDC673","#8B864E","#F0F8FF","#8A2BE2","#5F9EA0","#98F5FF","#8EE5EE","#7AC5CD",
"#53868B","#6495ED","#00008B","#008B8B","#483D8B","#00CED1","#00BFFF","#00B2EE","#009ACD","#00688B","#1E90FF","#1C86EE","#1874CD","#104E8B","#ADD8E6","#BFEFFF",
"#B2DFEE","#9AC0CD","#68838B","#E0FFFF","#D1EEEE","#B4CDCD","#7A8B8B","#87CEFA","#B0E2FF","#A4D3EE","#8DB6CD","#607B8B","#8470FF","#B0C4DE","#CAE1FF","#BCD2EE",
"#A2B5CD","#6E7B8B","#66CDAA","#0000CD","#7B68EE","#48D1CC","#191970","#000080","#AFEEEE","#BBFFFF","#AEEEEE","#96CDCD","#668B8B","#B0E0E6","#4169E1","#4876FF",
"#436EEE","#3A5FCD","#27408B","#87CEEB","#87CEFF","#7EC0EE","#6CA6CD","#4A708B","#6A5ACD","#836FFF","#7A67EE","#6959CD","#473C8B","#4682B4","#63B8FF","#5CACEE",
"#4F94CD","#36648B","#7FFFD4","#76EEC6","#458B74","#F0FFFF","#E0EEEE","#C1CDCD","#838B8B","#0000FF","#0000EE","#00FFFF","#00EEEE","#00CDCD","#40E0D0","#00F5FF",
"#00E5EE","#00C5CD","#00868B","#8B008B","#9932CC","#BF3EFF","#B23AEE","#9A32CD","#68228B","#9400D3","#FFF0F5","#EEE0E5","#CDC1C5","#8B8386","#BA55D3","#E066FF",
"#D15FEE","#B452CD","#7A378B","#9370DB","#AB82FF","#9F79EE","#8968CD","#5D478B","#E6E6FA","#FF00FF","#EE00EE","#CD00CD","#B03060","#FF34B3","#EE30A7","#CD2990",
"#8B1C62","#DA70D6","#FF83FA","#EE7AE9","#CD69C9","#8B4789","#DDA0DD","#FFBBFF","#EEAEEE","#CD96CD","#8B668B","#A020F0","#9B30FF","#912CEE","#7D26CD","#551A8B",
"#D8BFD8","#FFE1FF","#EED2EE","#CDB5CD","#8B7B8B","#EE82EE","#8B0000","#FF1493","#EE1289","#CD1076","#8B0A50","#FF69B4","#FF6EB4","#EE6AA7","#CD6090","#8B3A62",
"#CD5C5C","#FF6A6A","#EE6363","#CD5555","#8B3A3A","#FFB6C1","#FFAEB9","#EEA2AD","#CD8C95","#8B5F65","#C71585","#FFE4E1","#EED5D2","#CDB7B5","#8B7D7B","#FF4500",
"#EE4000","#CD3700","#8B2500","#DB7093","#FF82AB","#EE799F","#CD6889","#8B475D","#D02090","#FF3E96","#EE3A8C","#CD3278","#8B2252","#B22222","#FF3030","#EE2C2C",
"#CD2626","#8B1A1A","#FFC0CB","#FFB5C5","#EEA9B8","#CD919E","#8B636C","#FF0000","#EE0000","#CD0000","#FF6347","#EE5C42","#CD4F39","#8B3626","#FF8C00","#FF7F00",
"#EE7600","#CD6600","#8B4500","#E9967A","#F08080","#FFA07A","#EE9572","#CD8162","#8B5742","#FFDAB9","#EECBAD","#CDAF95","#8B7765","#FFE4C4","#EED5B7","#CDB79E",
"#8B7D6B","#FF7F50","#FF7256","#EE6A50","#CD5B45","#8B3E2F","#F0FFF0","#E0EEE0","#C1CDC1","#838B83","#FFA500","#EE9A00","#CD8500","#8B5A00","#FA8072","#FF8C69",
"#EE8262","#CD7054","#8B4C39","#A0522D","#FF8247","#EE7942","#CD6839","#8B4726","#FFEBCD","#D9D919","#B8860B","#FFB90F","#EEAD0E","#CD950C","#8B6508","#FFFACD","#EEE9BF",
"#CDC9A5","#8B8970","#EEDD82","#FFEC8B","#EEDC82","#CDBE70","#8B814C","#FAFAD2","#FFFFE0","#EEEED1","#CDCDB4","#8B8B7A","#EEE8AA","#FFEFD5","#FFF8DC","#EEE8CD",
"#CDC8B1","#8B8878","#FFD700","#EEC900","#CDAD00","#8B7500","#DAA520","#FFC125","#EEB422","#CD9B1D","#8B6914","#FFE4B5","#FFFF00","#EEEE00","#CDCD00","#8B8B00",
"#BC8F8F","#FFC1C1","#EEB4B4","#CD9B9B","#8B6969","#8B4513","#F4A460","#F5F5DC","#A52A2A","#FF4040","#EE3B3B","#CD3333","#8B2323","#DEB887","#FFD39B","#EEC591",
"#CDAA7D","#8B7355","#D2691E","#FF7F24","#EE7621","#CD661D","#CD853F","#D2B48C","#FFA54F","#EE9A49","#8B5A2B","#2F4F4F","#97FFFF","#8DEEEE","#79CDCD","#528B8B",
"#696969","#D3D3D3","#778899","#708090","#C6E2FF","#B9D3EE","#9FB6CD","#6C7B8B","#BEBEBE","#000000","#030303","#050505","#080808","#0A0A0A","#0D0D0D","#0F0F0F",
"#121212","#141414","#171717","#1A1A1A","#1C1C1C","#1F1F1F","#212121","#242424","#262626","#292929","#2B2B2B","#2E2E2E","#303030","#333333","#363636","#383838",
"#3B3B3B","#3D3D3D","#404040","#424242","#454545","#474747","#4A4A4A","#4D4D4D","#4F4F4F","#525252","#545454","#575757","#595959","#5C5C5C","#5E5E5E","#616161",
"#636363","#666666","#6B6B6B","#6E6E6E","#707070","#737373","#757575","#787878","#7A7A7A","#7D7D7D","#7F7F7F","#828282","#858585","#878787","#8A8A8A","#8C8C8C",
"#8F8F8F","#919191","#949494","#969696","#999999","#9C9C9C","#9E9E9E","#A1A1A1","#A3A3A3","#A6A6A6","#A8A8A8","#ABABAB","#ADADAD","#B0B0B0","#B3B3B3","#B5B5B5",
"#B8B8B8","#BABABA","#BDBDBD","#BFBFBF","#C2C2C2","#C4C4C4","#C7C7C7","#C9C9C9","#CCCCCC","#CFCFCF","#D1D1D1","#D4D4D4","#D6D6D6","#D9D9D9","#DBDBDB","#DEDEDE",
"#E0E0E0","#E3E3E3","#E5E5E5","#E8E8E8","#EBEBEB","#EDEDED","#F0F0F0","#F2F2F2","#F5F5F5","#F7F7F7","#FAFAFA","#FCFCFC","#FFFFFF","#FAEBD7","#FFEFDB","#EEDFCC",
"#CDC0B0","#8B8378","#FFFAF0","#F8F8FF","#FFDEAD","#EECFA1","#CDB38B","#8B795E","#FDF5E6","#DCDCDC","#FFFFF0","#EEEEE0","#CDCDC1","#8B8B83","#FAF0E6","#FFF5EE",
"#EEE5DE","#CDC5BF","#8B8682","#FFFAFA","#EEE9E9","#CDC9C9","#8B8989","#F5DEB3","#FFE7BA","#EED8AE","#CDBA96","#8B7E66","#20343c4f","#C6E0F3","#5C3317","#B5A642",
"#8C7853","#D98719","#B87333","#DC143C","#5C4033","#A9A9A9","#4A766E","#871F78","#8FBC8B","#97694F","#855E42","#856363","#F5CCCC","#D19275","#527F76","#215E21",
"#4B0082","#E9C2A6","#E47833","#EAEAAE","#9370D8","#A68064","#23238E","#4E4EFF","#FF6EC7","#00009C","#EBC79E","#CFB53B","#D87093","#D9D9F3","#5959AB","#8C1717",
"#6B4226","#FF1CAE","#38B0DE","#CDCDCD",)



class color_select(Screen):
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFScatset.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFScatset.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFScatset.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session, scolor=None,t_farb1=0xffffff,t_farb2=0xff0000,kat=None,args = None):
		self.session = session
		Screen.__init__(self, session)
		self.skinName="PFS_categorie_conf5"
		self["catmenu"] = List([])
		self["catmenu"].style="colorsx"
		self["key_green"] = Label()
		self["key_red"] = Label()
		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		calist=[]
		i=0
		self.sel_index=0
		for x in pfscolor_list:
			color= int(x.lstrip('#'), 16)
			tx1= " "
			tx2= " "
			if scolor != None and scolor==color:
				self.sel_index=i
				tx1= " >> "
				tx2= " << "
			calist.append((tx1,tx2, color, color,x,t_farb1,t_farb2,_("calendar days"),_("calendar holiday")))
			i+=1
		if kat:
			self.setTitle(_("Select Color for: ")+kat)
		self["catmenu"].setList(calist) 
		self.onLayoutFinish.append(self.move)
		
		self["actions"] = ActionMap(["OkCancelActions","ColorActions"], 
		{
			"ok": self.keyOK,
			"cancel": self.cancel,
		}, -1)

	def move(self):
		self['catmenu'].setIndex(self.sel_index)

	def keyOK(self):
		current = self["catmenu"].getCurrent()
		if current:
			ce = current[4]
			self.close(ce)

	def cancel(self):
		self.close(None)




class PFS_categorie_conf7(Screen, HelpableScreen):
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFScatset.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFScatset.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFScatset.xml"
	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session):
		color_holiday = "#FF0000"
		color_days = "#FFFFFF"
		color_event = "#e5b243"
		inactiv_timer = "#FFFFFF"
		cal_background="#20343c4f"
		col_list_jubi = "#FF0000"
		col_list_txt = "#FFFFFF"
		self.alt_list=[]
		self.z_liste=["0","1","0","1","1","0","0","0","0","0"]
		categories="" #",".join((_("None"),_("None"),_("None"),_("None"),_("None"),_("None"),_("None"),_("None"),_("None"),_("None"), _("calendar days"),_("calendar holiday"),_("calendar day background"),_("calendar day event"),_("list inactive"),_("list anniversaries"),_("list txt"),_("calendar today background")))
		mcolor_list=() 
		if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
			configparser = ConfigParser()
			configparser.read("/etc/ConfFS/PlanerFS.conf")
			if configparser.has_section("settings"):
				l1=configparser.items("settings")
				for k,v in  l1:
					if k=="categories":
						categories=str(v)
					elif k=="z_liste":
						self.z_liste=list(v.split(","))
					elif k=="cat_color_list":
						mcolor_list=v.split(",")
		cats= categories.split(",")
		self.categories= list(cats)
		self.color_list=list(mcolor_list)
		allcolor_list=["#00008B","#D2691E","#006400","#696969","#FFD700","#000000","#B22222","#8B8878","#CD0000","#00868B","#f0f8ff","#ff4500","#20343c4f","#deb887","#228B22","#5F9EA0","#DC143C","#F0F8FF","#EEC900","#20343c4f","#f0f8ff","#000000","#FFFFFF"]
		if len(self.color_list)<23:
			self.color_list.extend(allcolor_list[len(self.color_list):])
		if len(self.categories)<10:
			self.categories=[_("None"),_("Birthday"), _("HOLIDAY"), _("Anniversary"), _("Wedding day"),_("None"),_("None"),_("None"),_("None"),_("None")]
		self.categories.extend((_("calendar days"),_("calendar holiday"),_("calendar background"),_("calendar event"),_("calendar today background"),_("list inactive"),_("list anniversaries"),_("list text"),_("list heading"),_("startscreen background"),_("startscreen text"),_("calendar week background"),_("calendar week text")))

		Screen.__init__(self, session)
		self.skinName="PFS_categorie_conf5"
		HelpableScreen.__init__(self)
		self.setTitle(_("Edit colors and categories"))
		self.list=[]
		self["catmenu"] = List([])

		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("Years"))
		self["key_blue"] = Label(_("Color"))
		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions", 
		{
			"cancel": (self.cancel,_("Cancel")),
			"ok": (self.text,_("Edit text for categorie")),
		})

		self["ColorActions"] = HelpableActionMap(self,  "ColorActions",
		{
			"green": (self.save,_("Save and exit")),
			"red": (self.cancel,_("Cancel")),
			"yellow": (self.red2,_("Toggle number of years")),
			"blue": (self.colors,_("Open color list")),
		})

		self.alt_list=[]
		self.alt_list.extend(self.categories)
		self.alt_list.extend(self.color_list)
		self.alt_list.extend(self.z_liste)
		self.onLayoutFinish.append(self.load_list)

	def load_list(self,ind=0):
		liste=[]
		text_col=self.color_list[10]
		bg_col=self.color_list[12]
		self.t_farb1=int(text_col.lstrip('#'), 16)
		self.t_farb2=int(bg_col.lstrip('#'), 16)
		for x in range(len(self.color_list)):
			try:  
				text=  _(self.categories[x])
				zaehle=", "+_("Not number of years")
				if x<10:
					if self.z_liste[x]=="1":
						zaehle=", "+_("Number of years")
					text=_("Category")+": "+ _(self.categories[x])+ zaehle
				liste.append((_(self.categories[x]),self.color_list[x],text)) 
			except:
				pass
		alist=[]
		for x in liste:
			txtcol=int(text_col.lstrip('#'), 16)
			bgcol= int(bg_col.lstrip('#'), 16)
			if x[0] ==_("calendar days"):
				txtcol= int(x[1].lstrip('#'), 16)
				self.t_farb1=txtcol
			elif x[0] ==_("startscreen background") or x[0] ==_("startscreen text"):
				txtcol= int(self.color_list[20].lstrip('#'), 16)
				bgcol=  int(self.color_list[19].lstrip('#'), 16)
			elif x[0] ==_("calendar holiday"):
				txtcol= int(x[1].lstrip('#'), 16)
				self.t_farb2= txtcol
			elif x[0] ==_("calendar week text") or x[0] ==_("calendar week background"):
				txtcol= int(self.color_list[22].lstrip('#'), 16)
				bgcol=  int(self.color_list[21].lstrip('#'), 16)
			elif x[0] in (_("list inactive"),_("list anniversaries"),_("list text"),_("list heading")):
				bgcol= bgcol
				txtcol= int(x[1].lstrip('#'), 16)
			else:
				bgcol= int(x[1].lstrip('#'), 16)

			res=(" text",x[2],txtcol,bgcol,x)
			alist.append(res)
		self["catmenu"].setList(alist)
		self['catmenu'].setIndex(ind)

	def colors(self):
		farb=self["catmenu"].getCurrent()[4][1]
		farb=int(farb.lstrip('#'), 16)
		self.session.openWithCallback(self.color_set, color_select,farb, self.t_farb1,self.t_farb2,self["catmenu"].getCurrent()[4][0])    
	def color_set(self,answer=None):
		if answer:
			idx =self["catmenu"].getIndex()
			self.color_list[idx]=answer
			self.load_list(idx)

	def text(self):
		if self["catmenu"].getIndex()<10:   
			text1=self["catmenu"].getCurrent()[4][0]
			self.session.openWithCallback(self.text_set,VirtualKeyBoard, title=_("Edit text for category"), text=text1)

	def red2(self):
		if self["catmenu"].getIndex()<10:
			ind=self["catmenu"].getIndex()
			if self.z_liste[ind]=="1":
				self.z_liste[ind]="0"
			else:
				self.z_liste[ind]="1"
			self.load_list(ind)
			
	def text_set(self,answer=None):
		if answer:
			idx =self["catmenu"].getIndex()
			self.categories[idx]=answer
			self.load_list(idx)


	def save(self):
		self.configparser2 = ConfigParser()
		self.configparser2.read("/etc/ConfFS/PlanerFS.conf")
		cat=self.categories[0:10]
		self.catego=",".join(cat)
		self.col=",".join(self.color_list)
		zz=",".join(self.z_liste)
		if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
			self.configparser2.set("settings", "categories",str(self.catego.encode("UTF-8")))
			self.configparser2.set("settings", "cat_color_list",self.col)
			self.configparser2.set("settings", "z_liste",zz)
		fp = open("/etc/ConfFS/PlanerFS.conf","w")
		self.configparser2.write(fp)
		self.new_list=[]
		self.new_list.extend(self.categories)
		self.new_list.extend(self.color_list)
		self.new_list.extend(self.z_liste)
		if self.alt_list != self.new_list:
			self.session.openWithCallback(self.saveConfirm,MessageBox,_("Restart PlanerFS for new settings\nPlease wait a moment"),MessageBox.TYPE_INFO, timeout = 5)
		else:
			self.close(None)

	def saveConfirm(self,answer=None):
		self.close(True,self.session,"restart")

	def cancel(self):
		self.close(None)



class schicht_conf(Screen, HelpableScreen):
	global L4l
	try:
		from Plugins.Extensions.LCD4linux.module import L4Lelement
		L4l=True
	except:
		L4l=None        
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFScatset.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFScatset.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFScatset.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session):
		self.schicht_colors={"F":"#008B45","S":"#FFD700","N":"#3A5FCD","fr":"#858585"}
		l4l_sets=("Off","1","1","0","80","500","100","10","On,Idle")
		schicht=("0","0","0")
		configparser = ConfigParser()
		configparser.read("/etc/ConfFS/PlanerFS.conf")

		if configparser.has_section("settings"):
			if configparser.has_option("settings","schicht_art"):
				schicht=str(configparser.get("settings","schicht_art")).split(",")
				if len(schicht)<3:
					schicht.extend(("0","0","0")[len(schicht):])
			if configparser.has_option("settings","schicht_col"):
				self.schicht_colors= eval(configparser.get("settings","schicht_col"))
			else:
				self.schicht_colors={"F":"#008B45","S":"#FFD700","N":"#3A5FCD","fr":"#858585"}
			if configparser.has_option("settings","l4l_sets"):
				l4l_sets= configparser.get("settings","l4l_sets").split(":")
			else:
				l4l_sets=("On","1","1","0","80","500","100","10","On,Idle","0")


		schicht_des=int(schicht[2])
		if not _("without text") in self.schicht_colors:
			self.schicht_colors[_("without text")]="#858585"
		if schicht_des and not _("If description") in self.schicht_colors:
			self.schicht_colors[_("If description")]="#858585"
		elif schicht_des==0 and  _("If description") in self.schicht_colors:
			del self.schicht_colors[_("If description")]
		if _("unlisted") in self.schicht_colors: 
			del self.schicht_colors[_("unlisted")]
		Screen.__init__(self, session)
		self.skinName="PFS_categorie_conf5"
		HelpableScreen.__init__(self)
		self.setTitle(_("Setting shifts"))
		self.list=[]
		self["catmenu"] = List([])
		self["catmenu"].style="schicht"
		self.idx=0
		self.lcl_sets2=list(l4l_sets)
		if len(self.lcl_sets2)==9:self.lcl_sets2.append("0")
		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("delete"))
		self["key_blue"] = Label(_("New"))

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions", 
		{
			"cancel": (self.cancel,_("Cancel")),
			"ok": (self.text,_("Edit selected option")),
		})

		self["ColorActions"] = HelpableActionMap(self,  "ColorActions",
		{
			"green": (self.save,_("Save and exit")),
			"red": (self.cancel,_("Cancel")),
			"yellow": (self.del_entry,_("delete shift entry")),
			"blue": (self.new_entry,_("Make new entry")),
		})
		self["catmenu"].onSelectionChanged.append(self.changed)
		self.onLayoutFinish.append(self.load_list)

	def changed(self):
		if self["catmenu"].getCurrent()[4] == "sch_col":
			self["key_yellow"].show()
			self["key_blue"].show()
		else:
			self["key_yellow"].hide()
			self["key_blue"].hide()
	def load_list(self):
		liste=[]
		self.farb_start=2
		txtcol="#ffffff"
		bgcol="#000000"
		txtcol=int(txtcol.lstrip('#'), 16)
		bgcol=None
		liste.append((" >> "+_("Shift colors:"),"",txtcol,bgcol,"sch_col",""))
		colb=[]
		for key,v  in self.schicht_colors.items():
			if key not in colb:   
				colb.append(key)
				liste.append((key,"",txtcol,int(v.lstrip('#'), 16),"sch_col",(key,v)))
		if L4l:
			liste.append((" ","",txtcol,bgcol,"",""))
			liste.append((_(" >> l4l-Grafik:"),"",txtcol,bgcol,""))
			liste.append((_("Show in LCD"),self.lcl_sets2[0],txtcol,bgcol,0))
			liste.append((_("LCD"),self.lcl_sets2[1],txtcol,bgcol,1))
			liste.append((_("Screen"),self.lcl_sets2[2],txtcol,bgcol,2))
			liste.append((_("Mode"),self.lcl_sets2[8],txtcol,bgcol,8))
			liste.append((_("Widht total"),self.lcl_sets2[5],txtcol,bgcol,5))
			liste.append((_("High total"),self.lcl_sets2[6],txtcol,bgcol,6))
			liste.append((_("Distance from top (pixel)"),self.lcl_sets2[3],txtcol,bgcol,3))
			liste.append((_("Distance from left (%)"),self.lcl_sets2[9],txtcol,bgcol,9))
			liste.append((_("Size for a single"),self.lcl_sets2[4],txtcol,bgcol,4))
			liste.append((_("distance between"),self.lcl_sets2[7],txtcol,bgcol,7))
		self["catmenu"].setList(liste)

	def colors(self):
		if self["catmenu"].getCurrent()[5] and len(self["catmenu"].getCurrent()[5])>1:
			farb=self["catmenu"].getCurrent()[5][1]
			farb=int(farb.lstrip('#'), 16)
			self.t_farb1=int("#000000".lstrip('#'), 16)
			self.t_farb2=None
			self.session.openWithCallback(self.sch_col_set, color_select,farb, self.t_farb1,self.t_farb2,self["catmenu"].getCurrent()[5][0])

	def sch_col_set(self,answer=None):
		if answer:
			if str(self["catmenu"].getCurrent()[4]) == "sch_col":
				self.schicht_colors[self["catmenu"].getCurrent()[0]]=answer.lstrip('#')
			self.load_list()

	def text(self):
		if self["catmenu"].getCurrent()[4] == "sch_col":
			self.colors()
		elif self["catmenu"].getCurrent()[0].strip() != "": 
			auswahl=self["catmenu"].getCurrent()[0]
			if auswahl == _("Show in LCD"): 
				self.session.openWithCallback(self.choice_back, ChoiceBox, title=_("Show on LCD"), list=((_("activate"),"On"),(_("deactivate"),"Off")))
			elif auswahl == _("LCD"): 
				self.session.openWithCallback(self.choice_back, ChoiceBox, title=_("Select the LCD"), list=(("1","LCD 1"),("LCD 2","2"),("LCD 3","3")))
			elif auswahl == _("Screen"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set number for screen")),text = self.lcl_sets2[2],maxSize = False,type=Input.NUMBER)
			elif auswahl == _("Mode"): 
				self.session.openWithCallback(self.choice_back, ChoiceBox, title=_("Select the Mode(s)"), list=(("On","On"),("Idle","Idle"),("Media","Media"),("On,Media","On,Media"),("Idle,Media","Idle,Media"),("On,Idle","On,Idle"),("On,Idle,Media","On,Idle,Media")))
			elif auswahl == _("Widht total"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set Widht total")),text = self.lcl_sets2[5],maxSize = False,type=Input.NUMBER)
			elif auswahl == _("High total"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set High total")),text = self.lcl_sets2[4],maxSize = False,type=Input.NUMBER)
			elif auswahl == _("Distance from left (%)"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set Distance from left (%)")),text = self.lcl_sets2[9],maxSize = False,type=Input.NUMBER)
			elif auswahl == _("Distance from top (pixel)"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set Distance from top in pixel")),text = self.lcl_sets2[3],maxSize = False,type=Input.NUMBER)
			elif auswahl == _("Size for a single"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set Size for a single")),text = self.lcl_sets2[4],maxSize = False,type=Input.NUMBER)
			elif auswahl == _("distance between"): 
				self.session.openWithCallback(self.texteingabeFinished,InputBox,title = (_("Set distance between")),text = self.lcl_sets2[7],maxSize = False,type=Input.NUMBER)




	def choice_back(self,answer=None):
		if answer:
			self.lcl_sets2[self["catmenu"].getCurrent()[4]] =answer[1]
			self.load_list()

	def texteingabeFinished(self,answer=None):
		if answer:
			self.lcl_sets2[self["catmenu"].getCurrent()[4]] =answer
			self.load_list()


	def del_entry(self):
		if self["catmenu"].getCurrent()[4] == "sch_col":
			x=self["catmenu"].getCurrent()[5]
			del self.schicht_colors[x[0]]
			self.load_list()

	def new_entry(self):
		self.session.openWithCallback(self.new_entry2,VirtualKeyBoard,title = _("New entry"),text="")

	def new_entry2(self,answer):
		if answer:
			if not answer in self.schicht_colors:
				self.schicht_colors[answer.strip()]= "858585"
				self.load_list() 
			else:
				self.session.open(MessageBox, "entry already exists", type=MessageBox.TYPE_ERROR)

	def save(self):
		configparser2 = ConfigParser()
		configparser2.read("/etc/ConfFS/PlanerFS.conf")
		if not configparser2.has_section("settings"):
			configparser2.add_section("settings")
		configparser2.set("settings", "schicht_col",str(self.schicht_colors))
		if L4l:configparser2.set("settings","l4l_sets", ':'.join(map(str, self.lcl_sets2)))
		fp = open("/etc/ConfFS/PlanerFS.conf","w")
		configparser2.write(fp)
		self.close()

	def cancel(self):
		self.close()
