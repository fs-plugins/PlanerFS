# -*- coding: utf-8 -*-
from . import _
import datetime
import re
import base64
class Cards_parse():

	def parseCards(self, lines, index=None):
		name = ''
		mask={}
		zus_list=[]
		mask['N']=re.compile("^N(.*).*")
		mask['FN']=re.compile("^FN:(.*)")
		mask['ADR']=re.compile("^ADR;.*:(.*).*")
		mask['MAIL']=re.compile("^EMAIL;.*:(.*).*")
		mask['BDAY']=re.compile("^BDAY:(.*).*")
		mask['TEL']=re.compile("^TEL;.*:(.*).*")
		mask['NICKNAME']=re.compile("^NICKNAME:(.*).*")
		mask['PHOTO']=re.compile("^PHOTO;(.*).*")
		mask['LABEL']=re.compile("^LABEL;(.*).*")
		mask['MAILER']=re.compile("^MAILER:(.*).*")
		mask['TZ']=re.compile("^TZ;(.*).*")
		mask['GEO']=re.compile("^GEO:(.*).*")
		mask['TITLE']=re.compile("^TITLE:(.*).*")
		mask['ROLE']=re.compile("^ROLE:(.*).*")
		mask['LOGO']=re.compile("^LOGO;(.*).*")
		mask['AGENT']=re.compile("^AGENT;(.*).*")
		mask['ORG']=re.compile("^ORG:(.*).*")
		mask['CATEGORIES']=re.compile("^CATEGORIES:(.*).*")
		mask['NOTE']=re.compile("^NOTE:(.*).*")
		mask['PRODID']=re.compile("^PRODID:(.*).*")
		mask['REV']=re.compile("^REV:(.*).*")
		mask['SORT-STRING']=re.compile("^SORT-STRING:(.*).*")
		mask['SOUND']=re.compile("^SOUND;(.*).*")
		mask['UID']=re.compile("^UID:(.*).*")
		mask['URL']=re.compile("^URL:(.*).*")
		mask['VERSION']=re.compile("^VERSION:(.*).*")
		mask['CLASS']=re.compile("^CLASS:(.*).*")
		mask['KEY']=re.compile("^KEY;(.*).*")
		mask['NOTE']=re.compile("^NOTE;(.*).*")

		count = range(1, len(lines))
		for i in count:
			data = lines[i]
			if data.startswith(' '):
				lines[i-1]= lines[i-1].strip('\r\n') + lines[i].lstrip()
				del lines[i]
				count.insert(i,i)
				count.pop()
		fn = ["FN",""]
		n =["N",""]
		mail = ["EMAIL;PREF;INTERNET"," "]
		bday=["BDAY","0-1-1"]
		tel_list=[]
		adr_home=["ADR;HOME",";;;;;;"]
		adr_work=["ADR;WORK",";;;;;;"]
		NICKNAME=""
		jpg=("","","")
		LABEL=""
		MAILER=""
		TZ=""
		GEO=""
		TITLE=""
		ROLE=""
		LOGO=""
		AGENT=""
		ORG=""
		CATEGORIES=""
		NOTE=""
		PRODID=""
		REV=""
		SORTSTRING=""
		SOUND=""
		UID=""
		URL=""
		VERSION=""
		CLASS=""
		KEY=""
		tel_n=1
		notiz=""
		sortname=""
		for line in lines:
			try:
				line=line.encode("UTF-8")
			except:
				line=line.decode("iso-8859-1").encode("UTF-8")
			if mask['N'].match(line):
				a=mask['N'].match(line).group(0).split(":")
				n = (a[0],a[1].strip('\r\n').strip())
				sortname=n[1].replace("ä","ae").replace("Ä","ae").replace("ö","Oe").replace("Ö","oe").replace("ü","ue").replace("Ü","ue")
			elif mask['FN'].match(line):
					summary = mask['FN'].match(line).group(1)
					summary = str(summary.strip('\r\n').strip())
					a=mask['FN'].match(line).group(0).split(":")
					fn = (a[0],summary)
			elif mask['NOTE'].match(line):
					summary = mask['NOTE'].match(line).group(1)
					summary = str(summary.strip('\r\n').strip())
					a=mask['NOTE'].match(line).group(0).split(":")
					notiz = (a[0],summary)
			elif mask['ADR'].match(line):
					if "HOME" in mask['ADR'].match(line).group(0).upper():
						a=mask['ADR'].match(line).group(0).split(":")
						if len(a[1])>2:
							adr_home = (a[0],a[1].strip('\r\n'))
					elif "WORK" in mask['ADR'].match(line).group(0).upper():
						a=mask['ADR'].match(line).group(0).split(":")
						adr_work = (a[0],a[1].strip('\r\n'))
			elif mask['MAIL'].match(line):
					a=mask['MAIL'].match(line).group(0).split(":")
					mail = (a[0],a[1].strip('\r\n').strip())
			elif mask['BDAY'].match(line):
					a2="0-1-1"
					a=mask['BDAY'].match(line).group(0).split(":")
					if len(a[1].split("-"))<2:
						if len(a[1])>7:
							b=a[1].strip('\r\n').strip()
							a2=str(b[0:4])+"-"+str(b[4:6])+"-"+str(b[6:8])
					else:
						b=a[1].split("-")
						if len(b)==3:
							a2=str(b[0])+"-"+str(b[1])+"-"+str(b[2])
					bday = (a[0],a2)
			elif mask['PHOTO'].match(line):
					a2=mask['PHOTO'].match(line).group(0).split(":")
					if "jpg" in a2[0].lower() or "jpeg" in a2[0].lower():
						jpg=(a2[0],a2[1],"jpg")
					elif "png" in a2[0].lower():
						jpg=(a2[0],a2[1],"png")
					elif "bmp" in a2[0].lower():
						jpg=(a2[0],a2[1],"bmp")
					else:
						jpg=("","","")
			elif mask['TEL'].match(line):
					a_tel=mask['TEL'].match(line).group(0).split(":")
					if "HOME" in a_tel[0].upper():
						tel_list.append((_("HOME"),a_tel[0],a_tel[1].strip('\r\n').strip()))
					elif "CELL" in a_tel[0].upper():
						tel_list.append((_("MOBIL"),a_tel[0],a_tel[1].strip('\r\n').strip()))
					elif "WORK" in a_tel[0].upper():
						tel_list.append((_("WORK"),a_tel[0],a_tel[1].strip('\r\n').strip()))                                         
					elif "FAX" in a_tel[0].upper():
						tel_list.append((a_tel[0],a_tel[0],a_tel[1].strip('\r\n').strip()))
					elif "MSG" in a_tel[0].upper():
						tel_list.append((a_tel[0],a_tel[0],a_tel[1].strip('\r\n').strip()))
					elif "PAGER" in a_tel[0].upper():
						tel_list.append((a_tel[0],a_tel[0],a_tel[1].strip('\r\n').strip()))
					elif "BBS" in a_tel[0].upper():
						tel_list.append((a_tel[0],a_tel[0],a_tel[1].strip('\r\n').strip()))
					elif "MODEM" in a_tel[0].upper():
						tel_list.append((a_tel[0],a_tel[0],a_tel[1].strip('\r\n').strip()))
					else:
						tel_list.append(("Tel. "+str(tel_n),a_tel[0],a_tel[1].strip('\r\n').strip()))
					tel_n+=1
			else:
					zus_list.append(line)

			detail_list=(index,n,fn,adr_home,adr_work,mail,bday,tel_list,zus_list,sortname,jpg,notiz)
		return detail_list
