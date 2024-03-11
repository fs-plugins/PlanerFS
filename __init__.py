from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import sys, environ as os_environ
import gettext
from enigma import getDesktop

my_version="9.88"
dat_dir = "/etc/ConfFS/"
pyvers=sys.version_info[0]
DWide = getDesktop(0).size().width()
defconf = {
			"timestartstandby":"No",
			"startscreen_plus":"True",
			"timer_on":"On",
			"akt_intv":0,
			"m_dauer":0,
			"m_sound":"None",
			"m_sound_vol":"10,100",
			"autosync":"No",
			"cal_menu":1,
			"adr_menu":1,
			"adr_on":1,
			"startanzeige2":"systemstart",
			"start_display_autohide":0,
			"vorschaum":1,
			"kalender_art":"Gregorian",
			"holidays_in_startscreen":"Yes",
			"doubles_in_startscreen":"All",
			"starttime":"None",
			"altloesch_on":"No",
			"altloesch":365,
			"last Backup Path" :"/hdd/",
			"sec_file":"none",
			"extern_color":"On",
			"online_on_kal":1,
			"erinn_ext":1,
			"l4l_on":"No",
			"l4l_lcd":1,
			"l4l_screen":2,
			"l4l_font":40,
			"l4lm_font":60,
			"l4l_ges_file":"On",
			"l4l_ges_file_len":50,
			"m_radio_url":"",
			"schicht_send_url":"",
			"cals_dir":'',
			"ferien":0,
			"l_ferien":0,
			"start_back":"no_l",
			"bgr_skin":1,
			"schicht_art":"0,0,0,Schicht",
			"schicht_colors":{"F":"#008B45","S":"#FFD700","N":"#3A5FCD","fr":"#858585"},
			"z_liste": "0,1,0,1,1,0,0,0,0,0",
		}

def localeInit():
	lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
	os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
	gettext.bindtextdomain("PlanerFS", resolveFilename(SCOPE_PLUGINS, "Extensions/PlanerFS/locale"))

def _(txt):
	t = gettext.dgettext("PlanerFS", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)