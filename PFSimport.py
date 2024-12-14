# -*- coding: utf-8 -*-
from . import my_version, dat_dir, _
import os
import re
import os.path
from Screens.MessageBox import MessageBox
from time import *
import datetime
import codecs

import urllib
try:from configparser import ConfigParser#py3
except:from ConfigParser import ConfigParser

from .routines import Rules
from .routines_vc import Cards_parse
import ssl
import requests

altloesch=365
altloesch_on="No"

termindatei = "/etc/ConfFS/PlanerFS.ics"
if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
	configparser = ConfigParser()
	configparser.read("/etc/ConfFS/PlanerFS.conf")
	if configparser.has_section("settings"):
		if configparser.has_option("settings","altloesch_on"):
			altloesch_on=configparser.get("settings","altloesch_on")
		if configparser.has_option("settings","altloesch"): 
			altloesch=configparser.get("settings","altloesch")
#		if configparser.has_option("settings","cals_dir"): 
#			cals_dir=configparser.get("settings","cals_dir")
###############################################################################
class all_import():
	def run(self,imp_datei=None):
		self.ok=0
		if imp_datei != None:
			list1=[]
			list2=[]
			if os.path.exists(dat_dir+'PlanerFS.conf'):
				list1=self.einles(termindatei)
			list2=self.einles(imp_datei)
			if len(list2) > 0:
				list1.extend(list2)
				self.write_liste(list1)
		return self.ok

	def write_liste(self, liste):
		eventliste=liste
		events=[]
		ev_start="BEGIN:VCALENDAR\nMETHOD:PUBLISH\nPRODID: -EnigmaII-Plugin / PlanerFS "+my_version+"\nVERSION:2.0"
		events.append(ev_start)
		for x in eventliste:
			anzeige=""
			comment=""
			on="\nBEGIN:VEVENT\n"
			off="END:VEVENT"
			start_dat = strftime("DTSTART;TZID=Europe/Berlin:%Y%m%dT%H%M%S\n",strptime(str(x[2]), "%Y-%m-%d %H:%M:%S"))
			end_dat = strftime("DTEND;TZID=Europe/Berlin:%Y%m%dT%H%M%S\n",strptime(str(x[3]), "%Y-%m-%d %H:%M:%S"))
			self.altdatum = x[3]
			summary="SUMMARY:"+x[0]+"\n"
			desc=x[6]
			if x[6] is None or x[6]=="": desc=x[0]
			desc= "DESCRIPTION:"+desc+"\n"
			if x[1]=="TIMER":
				anzeige="BEGIN:VALARM\nACTION:"+str(x[4]) +"\nTRIGGER;VALUE=DURATION:-PT5M\n"+desc+"END:VALARM\n"
			elif x[4]=="DISPLAY":
				anzeige="BEGIN:VALARM\nACTION:DISPLAY\nTRIGGER;VALUE=DURATION:-P1D\n"+desc+"END:VALARM\n"
			cat="CATEGORIES:"+ str(x[1])+"\n"
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
				rule=rule+"\n"
			if x[10] and x[10] != None:
				comment="COMMENT:"+x[10]+"\n"
			detailliste=on+start_dat+end_dat+summary+cat+rule+desc+anzeige+comment+off
			if altloesch_on=="No":
				events.append(str(detailliste))
			else:
				if  self.altdatum >= self.altdat:
					events.append(str(detailliste))
				else:
					continue
			events.append("\nEND:VCALENDAR")
			f2=open(termindatei,"w")
			f2.writelines(events)
			f2.close()
			self.ok=1

	def einles(self,cal_datei):
		dataLines = None
		events=[]
		if os.path.isfile(cal_datei): 
			try:
				import icalendar
				parse1 = Rules().parseEvent_b(cal_datei)
				for x in parse1:
					r= x[3].date()
					if x[5] or x[3].date()>=datetime.datetime.today():
						events.append(x)
			except:
				dataLines = []
				tempFile = open(cal_datei, 'r')
				dataLines.extend(tempFile.readlines())
				tempFile.close()
		if dataLines:
			self.events = []
			mask = {}
			mask['umlaute'] = re.compile("(.*).*???????(.*).*")
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
					parse1 = Rules().parseEvent(eventLines,index,"")
					events.append(parse1)
					inEvent = False
					index+=1
				elif inEvent:
					eventLines.append(line)
			return events

cardfile = dat_dir+"PlanerFS.vcf"
class vcf_import():
	def run(self,imp_datei=None):
		self.ok=0
		if imp_datei != None:
			list1=[]
			list2=[]
			if os.path.exists(cardfile):
				list1=self.einles(cardfile)
				list2=self.einles(imp_datei)
				if len(list2) > 0:
					list1.extend(list2)
					f2=open(cardfile,"w")
					for x in list1:
						for x2 in x:
							f2.write(x2+"\n")
					f2.close()
					self.ok=1
		return self.ok

	def einles(self,vcf_datei):
		dataLines =[]
		if vcf_datei and os.path.isfile(vcf_datei):
			tempFile = open(vcf_datei, 'r')
			dataLines.extend(tempFile.readlines())
			tempFile.close()
		cards1 = []
		if dataLines:
			mask = {}

			mask['BEGIN'] = re.compile("^BEGIN:VCARD")
			mask['END'] = re.compile("^END:VCARD")
			inCard= False
			for line in dataLines: 
				line = line.strip('\r\n')
				if mask['BEGIN'].match(line):
					cardLines = ["BEGIN:VCARD"]
					inCard = True
				elif mask['END'].match(line) and inCard:
					cardLines.append("END:VCARD")
					cards1.append(cardLines)
					inCard = False
				elif inCard:
					cardLines.append(line)
		return cards1


class online_import():
	def run(self,datei=None,fer=None, nofer=1):
		opath=dat_dir+'PlanerFS_online.txt'
		if datei and os.path.exists(datei):opath=datei
		onl_lines=[]
		errmeld=None
		if nofer and os.path.exists(opath):
			with open(opath, 'r') as tempFile:
				onl_lines.extend(tempFile.readlines())
		ferien=fer
		if ferien is None and nofer is None:
			if os.path.exists(dat_dir+'PlanerFS.conf'):
				configparser = ConfigParser()
				configparser.read(dat_dir+"PlanerFS.conf")
				if configparser.has_option("settings","ferien"):
					f1=0
					f2="0"
					try:
						f1=int(configparser.get("settings","ferien"))
						if configparser.has_option("settings","l_ferien"):
							f2=configparser.get("settings","l_ferien")
					except:
						pass
					ferien=(f1,f2)
		if ferien and ferien[0]:
			try:
				from time import localtime
				jahr= localtime()[0]
				if int(ferien[1]) or (int(ferien[1]) == 0 and nofer is None):
					onl_lines.append("ferien"+" = https://www.schulferien.eu/downloads/ical4.php?land="+str(ferien[0])+"&type=1&year="+str(jahr))
				if int(ferien[1]) == 9 or nofer is None:
					onl_lines.append("ferien2"+" = https://www.schulferien.eu/downloads/ical4.php?land="+str(ferien[0])+"&type=1&year="+str(jahr+1))
			except:
				pass
		self.ok=0
		erg=1
		if len(onl_lines):
			try:
				context = ssl._create_unverified_context()
				ssl_context = True
			except:
				ssl_context = False
			for x in onl_lines:
				try:
					x=x.strip()
					url=None
					kalnum="1"
					if len(x) and not x.startswith("#"):
						spl = x.partition('=')
						if len(spl)==3:
							try:
								kt=spl[2].rpartition("=")
								kn=int(kt[2].strip())
								if kn==1 or kn==2:
									kalnum=kn
									url=kt[0].strip()
								else:
									url=spl[2].strip() 
							except:
								kalnum=1
								url=spl[2].strip()
							datei2=dat_dir+str(kalnum)+str(spl[0]).strip()+".ics"
						if url:
							try:
								headers = {
									'Accept': u"text/html,application/xhtml+xml,application/xml",
									'User-Agent': u"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
									'Accept-Encoding': u"gzip,deflate",
									'Accept-Language': u"en-US,en;q=0.8"
								}
								resp = requests.get(url, headers=headers, timeout=15, verify=False)
								status=resp.status_code
								if status==200:
									res = resp.content
									f=open(datei2,"wb")
									f.write(res)
									f.close()
									erg=2
								else:
									errmeld=str(status)+"\n"
									erg=0
							except Exception as e:
								errmeld=str(e)+"\n"
								erg=0
							if errmeld:
								fx=open("/tmp/PlanerFS-Errors.txt","a")
								fx.write("import1 read-error for: "+str(spl[0])+"\n"+" "*5+str(url)+"\n"+" "*5)
								fx.write(errmeld)
								fx.close()
								err=""
				except Exception as e:
					fx=open("/tmp/PlanerFS-Errors.txt","a")
					fx.write("import2 read-error for: "+str(x)+"\n"+str(e)+"\n")
					fx.close()
					continue

		return erg
