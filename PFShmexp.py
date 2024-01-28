from . import defconf
from time import localtime, time,mktime, timezone, altzone
import datetime
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser
from datetime import timedelta
import os
import re
import os.path

from .routines import Feiertage, Rules, Next_Termin, modul

conf=defconf

schicht_start=0
categories1=(_('Birthday'),_('Anniversary'),_('Wedding day'),'Birthday','Anniversary','Wedding day')
if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
	configparser = ConfigParser()
	configparser.read("/etc/ConfFS/PlanerFS.conf")
	if configparser.has_section("settings"):
		l1=configparser.items("settings")
		for k,v in  l1:
			if k in conf and v.strip() != "":
				if k=="categories":
					categories1=v.encode("UTF-8")
					categories1=list(categories1.split(","))
				else:
					try:
						conf[k] = int(v.strip())
					except:
						conf[k] = v.strip()        

schicht=str(conf["schicht_art"]).split(",")
if len(schicht)<3:schicht.extend(("0","0","0")[len(schicht):])

schicht_start=int(schicht[1])
class hm_exp(object):

	def get_calfiles(self):
		files=[]
		if conf["kalender_art"] != "Off":
			files.append(("Feiertage","Feiertage"))
		sond=[dat_dir]
		if conf["cals_dir"] and conf["cals_dir"] != "" and conf["cals_dir"] != dat_dir:sond=[dat_dir,conf["cals_dir"]]
		for xdir in sond:
			if os.path.exists(xdir):
				for cal_file in os.listdir(xdir):
					if cal_file.endswith(".ics"):
						nf_file= str(cal_file)[1:].replace(".ics","")
						if nf_file != "ferien" or conf["l_ferien"]:
							nf=(nf_file,xdir+cal_file)
							if not nf in files:files.append(nf)
#		if os.path.exists(conf["dat_dir"]):
#			for cal_file in os.listdir(conf["dat_dir"]):
#				if cal_file.endswith(".ics"):
#					nf=(str(cal_file).replace(".ics",""),conf["dat_dir"]+cal_file)
#					if not nf in files:files.append(nf)
#		for cal_file in os.listdir(conf["cals_dir"]):
#			if cal_file.endswith(".ics"):
#				nf_file= str(cal_file)[1:].replace(".ics","")
#				if nf_file != "ferien" or conf["l_ferien"]:
#					nf=(nf_file,conf["cals_dir"]+cal_file)
#					if not nf in files:files.append(nf)
		return(files)


	def get_caldates(self,vorsch=1,term_datei1=None):
		lt = localtime()
		self.monat=lt[1]
		self.jahr=lt[0]
		today=datetime.date.today()
		st2=localtime()
		self.altdat=today
		altjahr=self.altdat.year
		altmonat=self.altdat.month
		self.altdatum=datetime.date(altjahr,altmonat,1)
		if not isinstance(conf["schicht_col"], dict):
			conf["schicht_col"]=eval(conf["schicht_col"])
		self.schichtnamen=[]
		if isinstance(conf["schicht_col"], dict):
			for key in conf["schicht_col"].keys():
				self.schichtnamen.append(key)

		fileliste1=[]
		allterm=[]
		alltim=[]
		if term_datei1:
			fileliste1.append(("nix",term_datei1))
		else:
			fileliste1= self.get_calfiles()
		for term_datei in fileliste1:
			termd=term_datei[1]
			terminlist=[]
			timer_liste=[]
			self.events=[]
			if termd == "Feiertage":  
				monat=self.monat+int(vorsch)
				jahr=self.jahr
				if monat>12:
					monat=self.monat-12+int(vorsch)
					jahr=self.jahr+1
				end=datetime.date(jahr,monat,1)- datetime.timedelta(1)
				if conf["kalender_art"]=="Gregorian":
					self.bewegl_feiertage=Feiertage().ostern_greg(self.jahr)
					if int(end.year)>self.jahr:
						self.bewegl_feiertage.extend(Feiertage().ostern_greg(self.jahr+1))
				elif conf["kalender_art"]=="Julian":    
					self.bewegl_feiertage=Feiertage().ostern_jul(self.jahr)
					if int(end.year)>self.jahr:
						self.bewegl_feiertage.extend(Feiertage().ostern_jul(self.jahr+1))
				else:
					self.bewegl_feiertage=[]
				for x2 in self.bewegl_feiertage:
					if x2[3].date() >= self.altdatum:	
						next_date=(x2[3].year,x2[3].month,x2[3].day)
						y=(next_date,x2[0],x2[2],x2[1],x2[3])
						terminlist.append(y)

			elif termd:
				self.termindatei=termd
				if self.monat==12:
					sdt1=datetime.date(self.jahr+1, 1, 1)-datetime.timedelta(1)
				else:
					sdt1=datetime.date(self.jahr, self.monat+1, 1)-datetime.timedelta(1)
				self.monatstage=int(sdt1.day)
				dataLines = None
				if os.path.isfile(self.termindatei): 
					if modul:
						try:
							import icalendar
							parse1 = Rules().parseEvent_b(self.termindatei,self.schichtnamen)
							for x in parse1:
								if x[5] or x[3].date()>=today: 
									if x not in self.events:
										self.events.append(x)
   
						except Exception as e:
							dataLines = []
							tempFile = open(self.termindatei, 'rb')
							dataLines.extend(tempFile.readlines())
							tempFile.close()
					if dataLines:
						fname=str(self.termindatei).replace("/etc/ConfFS/","")
						self.events = []
						mask = {}
						mask['BEGIN'] = re.compile("^BEGIN:VEVENT")
						mask['END'] = re.compile("^END:VEVENT")
						inEvent= False
						index=0
						for line in dataLines: 
							line = line.replace("\r","")
							if mask['BEGIN'].match(line):
								eventLines = []
								inEvent = True
							elif mask['END'].match(line) and inEvent:
								parse1 = Rules().parseEvent(eventLines,index,fname,self.schichtnamen)
								if parse1[5] or parse1[3].date()>=today: 
									self.events.append(parse1)
									inEvent = False
								index+=1
							elif inEvent:
								eventLines.append(line)

		nowyear = today.year
		if self.altdatum <= datetime.date(self.jahr,self.monat,1):
			for x in self.events:
				sr=1
				if len(x)>16 and x[14]: sr=0
				if sr:
					y1=None
					y2=None
				try:
						next_datet=None
						if x[1] is None or x[1].lower() != "timer":
							zeit1=(x[2].hour,x[2].minute,"")
							next_datet = Next_Termin().next_termin(x[5], x[2], x[3],(lt[0],lt[1]),int(vorsch)+1,"hme",x[17])
							if next_datet and len(next_datet): 
								for z in next_datet:
									nd=z.date()
									if today <= nd:
										next_date=(z.year,z.month,z.day)
										date1=datetime.datetime(z.year,z.month,z.day,zeit1[0],zeit1[1])
										y1=(next_date,x[0],x[2],x[3],x[6],date1)
										terminlist.append(y1)
										if (x[15] or "DISPLAY" in str(x[4])):
											if x[15]:
												dr=x[15][0]
												date1=datetime.datetime(z.year,z.month,z.day,dr.hour,dr.minute)
												if x[15][2] and x[15][3]:
													if x[15][2]=="m":date1=date1-timedelta(minutes=x[15][3])
													elif x[15][2]=="h":date1=date1-timedelta(hours=x[15][3])
													elif x[15][2]=="d":date1=date1-timedelta(days=x[15][3])
											zeit1=(date1.hour,date1.minute)
											y2=(x[0],"DISPLAY",date1,zeit1,x[2],x[3])
											timer_liste.append(y2)
						else:
							if  not x[10] or x[10] != "no_activ":
								next_datet2=None
								now = datetime.datetime.now()
								next_datet2 = Next_Termin().next_termin(x[5], x[2], x[2],(lt[0],lt[1]),conf["vorschaum"]+1,"terminlist2",x[17])
								zeit1=(x[2].hour,x[2].minute)
								if next_datet2 and len(next_datet2): 
									for z in next_datet2:
										nd=z.date()
										if today+timedelta(2) < nd: 
											next_date=(z.year,z.month,z.day)
											date1=datetime.datetime(z.year,z.month,z.day,x[2].hour,x[2].minute)
											if x[15] or "DISPLAY" in str(x[4]):
												if x[15]:
													dr=x[15][0]
													date1=datetime.datetime(z.year,z.month,z.day,dr.hour,dr.minute)
													if x[15][2] and x[15][3]:
														if x[15][2]=="m":date1=date1-timedelta(minutes=x[15][3])
														elif x[15][2]=="h":date1=date1-timedelta(hours=x[15][3])
														elif x[15][2]=="d":date1=date1-timedelta(days=x[15][3])
											t2b=mktime(date1.timetuple())
											u = mktime(now.timetuple())
											if t2b-u>0:zeit1=(date1.hour,date1.minute)
											y2=(x[0],x[1],date1,zeit1,x[2],x[3])
											timer_liste.append(y2)
				except Exception as e:
						f2=open("/tmp/PlanerFS-Errors.txt","a")
						f2.write("schwerer Fehler:\n")
						f2.write(">> "+str(self.termindatei)+"\n")
						f2.write(str(x[0])+"\n")
						f2.write(str(e)+"\n")
						f2.close()
						continue



		if len(terminlist):allterm.extend(terminlist)
		if len(timer_liste):alltim.extend(timer_liste)

		return (allterm,alltim)

