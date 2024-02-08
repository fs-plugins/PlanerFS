from . import dat_dir,my_version, _
from Tools.LoadPixmap import LoadPixmap
from Screens.LocationBox import LocationBox
from Tools.Directories import *
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.FileList import FileList
from Components.Sources.List import List
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from enigma import getDesktop
from Components.config import ConfigLocations
import os.path
import urllib
from Tools.Directories import copyfile
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
from .PFSimport import all_import, vcf_import
last_backup_path="/"
internet_File=""
cals_dir=''
sec_file=None
adr_on=1

download_name="download"
if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
	configparser = ConfigParser()
	configparser.read("/etc/ConfFS/PlanerFS.conf")
	if configparser.has_section("settings"):
		if configparser.has_option("settings","last_backup_path"):
			last_backup_path=configparser.get("settings","last_backup_path")
		if configparser.has_option("settings","sec_file"):
			sec_file=configparser.get("settings","sec_file")
		if configparser.has_option("settings","cals_dir"):
			cals_dir=configparser.get("settings","cals_dir")
		if configparser.has_option("settings","adr_on"):
			adr_on=int(configparser.get("settings","adr_on"))
backup_path=ConfigLocations(default=[last_backup_path])


class PFS_filemenu7(Screen):
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFSmenulist.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFSmenulist.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFSmenulist.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()
	def __init__(self, session, startart=0):
		self.startart=startart
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.session = session
		self.settigspath = ""
		lista = []
		self["menulist"]=List([])
		self.num = 1
		lista.append(("1",_('Show list of all iCal-Files'), 'all_list'))
		lista.append(("2",_('backup files and settings'), 'backup'))
		lista.append(("3",_('restore files and settings'), 'restore'))
		lista.append(("4",_('delete extern ics-File'), 'delete'))
		lista.append(("5",_('Copy ics-File to PlanerFS path'), 'copy_in'))
		lista.append(("6",_('Copy ics-File of PlanerFS path'), 'copy_out'))
		lista.append(("7",_('Import all events from an ics file'), 'import_all'))
		nr=7
		if adr_on:
			lista.append(("8",_('Import all cards from an vcf file'), 'import_vcf'))
			nr=8
		if not os.path.exists('/etc/ConfFS/PlanerFS2.ics'):
			lista.append((str(nr+1),_('make second calendar'), 'make_sec'))
		self.setTitle("PlanerFS: "+_("Files Handling"))
		self["menulist"].setList(lista)

		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions","DirectionActions"],
		{
			"ok": self.run,
			"cancel": self.close,
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
		self.vcf=0
		returnValue = self["menulist"].getCurrent()[2]
		if returnValue == 'backup':
			self.backup()
		elif returnValue == 'restore':
			self.restore()
		elif returnValue == 'delete':
			self.del_1()
		elif returnValue == 'syncro':
			self.internet_import()
		elif returnValue == 'copy_in':
			self.copy_in()
		elif returnValue == 'copy_out':
			self.copy_out()
		elif returnValue == 'import_all':
			self.import_path()
		elif returnValue == 'import_vcf':
			self.vcf=1
			self.import_path()
		elif returnValue == 'make_sec':
			self.make_sec()
		elif returnValue == 'all_list':
			self.all_list()
		else:
			pass


	def pathsearch(self, path=None,ends=None,ausschl=None):
		file_list = []
		if path is not None:
			for found_file in os.listdir(path):
				if (ends==None or found_file.endswith(ends)) and (ausschl ==None or os.path.join(path,found_file) != ausschl):
					file_list.append((found_file,os.path.join(path,found_file)))
		return file_list

	def all_list(self):
		self.session.open(PFS_allfilelist)

	def make_sec(self):
		f=open('/etc/ConfFS/PlanerFS2.ics',"w")
		f.write("BEGIN:VCALENDAR\nMETHOD:PUBLISH\nPRODID: -EnigmaII-Plugin / PlanerFSsec "+my_version+"\nVERSION:2.0")
		f.write("\nEND:VCALENDAR")
		f.close()
		self.session.open(MessageBox,_("second calendar was created successfully, to see push-button Bouquet on the calendar") ,MessageBox.TYPE_INFO)
		self.close()

	def copy_in(self):
		self.session.openWithCallback(self.callCopy_in,BackupLocationBox,_("Please select source path..."),"","/tmp/",ConfigLocations(default=["/tmp/"]))

	def copy_out(self):
		cal_files_path = "/etc/ConfFS/"
		if os.path.exists(cal_files_path):
			cal_files = self.pathsearch(cal_files_path,".ics")
			if len(cal_files) > 0:
				self.session.open(del_files7,cal_files,"copy_out")
			else:
				self.session.open(MessageBox,_(_("No ics-File in this Path exist!")) ,MessageBox.TYPE_INFO)

	def import_path(self):
		self.session.openWithCallback(self.callImport,BackupLocationBox,_("Please select source path..."),"","/etc/ConfFS/",ConfigLocations(default=["/tmp/","/etc/ConfFS/"]))


	def callImport(self, path):
		if self.vcf==0:
			if path is not None and os.path.exists(path):
				cal_files = self.pathsearch(path,".ics","/etc/ConfFS/PlanerFS.ics")
				if len(cal_files) > 0:
					self.session.open(del_files7,cal_files,"importer")
					self.close()
				else:
					self.session.open(MessageBox,_("No ics-File in this Path exist!") ,MessageBox.TYPE_INFO)

		elif adr_on and self.vcf==1:
			if path is not None and os.path.exists(path):
					vcf_files = self.pathsearch(path,".vcf","/etc/ConfFS/PlanerFS.vcf")
					if len(vcf_files) > 0:
						self.session.open(del_files7,vcf_files,"importer_vcf")
						self.close()
					else:
						self.session.open(MessageBox,_("No vcf-File in this Path exist!") ,MessageBox.TYPE_INFO)

	def del_1(self):
		cal_files_path = "/etc/ConfFS/"
		if os.path.exists(cal_files_path):
			cal_files = self.pathsearch(cal_files_path,".ics","/etc/ConfFS/PlanerFS.ics")
			if len(cal_files) > 0:
				self.session.open(del_files7,cal_files,"delete")
			else:
				self.session.open(MessageBox,_("No extern ics-File exist!") ,MessageBox.TYPE_INFO)


	def callCopy_in(self, path):
		if path is not None and os.path.exists(path):
			cal_files = self.pathsearch(path,".ics")
			if len(cal_files) > 0:
				self.session.open(del_files7,cal_files,"copy_in")
			else:
				self.session.open(MessageBox,_("No ics-File in this Path exist!") ,MessageBox.TYPE_INFO)

	def backup(self):
		self.session.openWithCallback(self.callBackup,BackupLocationBox,_("Please select the backup path..."),"",last_backup_path,ConfigLocations(default=[last_backup_path]))

	def callBackup(self, path):
		if path is not None:
			if pathExists(path):
				last_backup_path = path
				conf_l=[]
				fp = file('/etc/ConfFS/PlanerFS.conf', 'r')
				conf_lines = fp.readlines()
				fp.close()
				for x in conf_lines:
					split = x.strip().split(' = ',1)
					if split[0] == "Backup Path": x = "Backup Path = "+last_backup_path
					conf_l.append(x)
				f=open("/etc/ConfFS/PlanerFS.conf","w")
				f.writelines(conf_l)
				f.close()
				self.settigspath = path + "ConfFS.tar.gz"
				if fileExists(self.settigspath):
					self.session.openWithCallback(self.callOverwriteBackup, MessageBox,_("Overwrite existing Backup?"),type = MessageBox.TYPE_YESNO,)
				else:
					com = "tar czvf %s /etc/ConfFS/" % (self.settigspath)
					self.session.open(Console,_("Backup ConfFS..."),[com])
			else:
				self.session.open(MessageBox,_("Directory %s nonexistent.") % (path),type = MessageBox.TYPE_ERROR,timeout = 5)

	def callOverwriteBackup(self, res):
		if res:
			com = "tar czvf %s /etc/ConfFS/" % (self.settigspath)
			self.session.open(Console,_("Backup Files and Settings..."),[com])

	def restore(self):
		self.session.openWithCallback(self.callRestore,BackupLocationBox,_("Please select the restore path..."),"",last_backup_path,ConfigLocations(default=[last_backup_path]))

	def callRestore(self, path):
		if path is not None:
			self.settigspath = path + "ConfFS.tar.gz"
			if fileExists(self.settigspath):
				self.session.openWithCallback(self.callOverwriteSettings, MessageBox,_("Overwrite existing Settings and Files?"),type = MessageBox.TYPE_YESNO,)
			else:
				self.session.open(MessageBox,_("File %s nonexistent.") % (path),type = MessageBox.TYPE_ERROR,timeout = 5)

	def callOverwriteSettings(self, res):
		if res:
			com = "cd /; tar xzvf %s" % (self.settigspath)
			self.session.open(Console,_("Restore Files and Settings..."),[com])

class BackupLocationBox(LocationBox):
	def __init__(self, session, text, filename, dir,  backup_path, minFree = None):
		inhibitDirs = ["/bin", "/boot", "/dev", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		LocationBox.__init__(self, session, text = text, filename = filename, currDir = dir, bookmarks = backup_path, autoAdd = True, editDir = True, inhibitDirs = inhibitDirs, minFree = minFree)
		self.skinName = "LocationBox"
class del_files7(Screen):
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFSmenulist.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFSmenulist.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFSmenulist.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session,cal_files,act):
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.session = session
		self.ext_file_list(cal_files)
		self["menulist"]=List([])
		self["menulist"].style="files"
		lista = self.cal_files
		self.act=act
		if self.act=="delete":
			self.setTitle("PlanerFS: "+_("delete extern ics-File"))
		elif self.act=="copy_in":
			self.setTitle("PlanerFS: "+_("Copy ics-File to PlanerFS path"))
		elif self.act=="copy_out":
			self.setTitle("PlanerFS: "+_("Copy ics-File of PlanerFS path"))
		elif self.act=="importer":
			self.setTitle("PlanerFS: "+_("Import all Data of ics-File"))
		elif adr_on and self.act=="importer_vcf":
			self.setTitle("PlanerFS: "+_("Import all Data of vcf-File"))
		self["menulist"].setList(lista)
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"ok": self.call_ok,
			"cancel": self.exit,
		}, -1)


	def call_ok(self):
		if self.act=="delete":
			self.del_file()
		elif self.act=="copy_in":
			self.cop_in()
		elif self.act=="copy_out":
			self.cop_out()
		elif self.act=="importer":
			self.import_all()
		elif self.act=="importer_vcf":
			self.import_vcf()
		else:
			pass

	def ext_file_list(self,cal_files):
		self.cal_files=[]
		for x in cal_files: 
			self.cal_files.append((x[0],x[1]))
		return self.cal_files

	def import_all(self):
		try:
			if self["menulist"].getCurrent()[0]:
				source=(self["menulist"].getCurrent()[1])
				importdatei = source
				imp=all_import().run(importdatei)
				if imp==1:
					self.session.open(MessageBox,_("Import completed successfully"), MessageBox.TYPE_INFO)
					self.exit()
				else:
					self.session.open(MessageBox,_("unknown error"), MessageBox.TYPE_ERROR)
		except Exception as e:
			self.writing(str(e))

	def import_vcf(self):
		if adr_on and self["menulist"].getCurrent()[0]:
			source=(self["menulist"].getCurrent()[1])
			importdatei = source
			imp=vcf_import().run(importdatei)
			if imp==1:
				self.session.open(MessageBox,_("Import completed successfully"), MessageBox.TYPE_INFO)
				self.exit()
			else:
				self.session.open(MessageBox,_("unknown error"), MessageBox.TYPE_ERROR)


	def cop_in(self):
		try:
			if self["menulist"].getCurrent()[0]:
				source=(self["menulist"].getCurrent()[1])
				target=os.path.join("/etc/ConfFS/",self["menulist"].getCurrent()[0])
				ret = copyfile(source, target)
				self.exit()
		except Exception as e:
			self.writing(str(e))

	def cop_out(self):
		self.session.openWithCallback(self.callCopy_out,BackupLocationBox,_("Please select the target path..."),"","/tmp/",ConfigLocations(default=["/tmp/"]))


	def callCopy_out(self, path):
		try:  
			if path is not None:
				if self["menulist"].getCurrent()[0]:
					source=(self["menulist"].getCurrent()[1])
					target= os.path.join(path,self["menulist"].getCurrent()[0])     
					ret = copyfile(source, target)
					self.exit()
		except Exception as e:
			self.writing(str(e))

	def del_file(self): 
		if self["menulist"].getCurrent()[0]:
			self.t=self["menulist"].getCurrent()
			text1=_("selceted File is:")+"\n"+self.t[0]+"\n\n"
			self.session.openWithCallback(self.del_file_ok,MessageBox,_(text1+_("Do you really want to delete this file?")) ,MessageBox.TYPE_YESNO)

	def del_file_ok(self,answer):
		try:
			os.unlink(self["menulist"].getCurrent()[1])
			self.session.openWithCallback(self.exit,MessageBox,(self.t[0]+"\n"+_("file is deleted")) ,MessageBox.TYPE_INFO)
		except OSError as e:
			txt= 'error: \n%s' % e
			self.session.openWithCallback(self.exit,MessageBox,txt ,MessageBox.TYPE_INFO)

	def writing(self,err=None):
		if err:
			f=open("/tmp/PlanerFS-Errors.txt","a")
			f.write("pfsfiles:\n"+err+"\n")
			f.close()
			self.session.open(MessageBox,_("unknown error"), MessageBox.TYPE_ERROR)

	def exit(self,answer=None):
		self.close() 

class PFS_allfilelist(Screen):
	DWide = getDesktop(0).size().width()
	if DWide < 800:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/SD/PFSmenulist.xml"
	elif DWide > 1300:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/fHD/PFSmenulist.xml"
	else:
		skindatei = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/skin/HD/PFSmenulist.xml"

	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()
	def __init__(self, session):
		liste=[]
		self.sliste=liste
		self["menulist"]=List([])
		self["menulist"].style="files"
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.setTitle("PlanerFS: "+_("Show list of all iCal-Files"))
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions","DirectionActions"],
		{
			"ok": self.nix,
			"cancel": self.close,
		}, -1)
		self.onLayoutFinish.append(self.read)

	def nix(self):
		pass

	def read(self):
		files=[]
		from .routines import readfiles
		files = readfiles(self,None,cals_dir)
		self["menulist"].setList(files)