# -*- coding: utf-8  -*-
from . import _
from time import localtime, strftime, strptime, strptime
from datetime import datetime, timedelta, date
import os
import re
from routines import Feiertage, Rules, Next_Termin
from ConfigParser import ConfigParser

conf = {
"vorschaum": 3,
"countdown": 0,
"sec_file": "",
"kalender_art": "Off",
"l4l_ges_file": "On",
"l4l_ges_file_len": 200,
"holidays_in_startscreen": "Yes",
"doubles": 0,
}
categories1 = (_('Birthday'), _('Anniversary'), _('Wedding day'), 'Birthday', 'Anniversary', 'Wedding day')
z_liste = ("0", "1", "1", "0", "1", "1", "0", "0", "0", "0")
if os.path.exists('/etc/ConfFS/PlanerFS.conf'):
    configparser = ConfigParser()
    configparser.read("/etc/ConfFS/PlanerFS.conf")
    if configparser.has_section("settings"):
        l1 = configparser.items("settings")
        for k, v in l1:
            if k == "cat_color_list":
                color_list = v.split(",")
            elif k == "z_liste":
                z_liste = list(v.split(","))
            elif k == "categories":
                categories1 = v.encode("UTF-8")
                categories1 = list(categories1.split(","))
            else:
                try:
                    conf[k] = int(v)
                except:
                    conf[k] = v

vorschaum = int(conf["vorschaum"])
#tmp_pruef=(_('Birthday'),_('Anniversary'),_('Wedding day'),'Birthday','Anniversary','Wedding day')
wochentage = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")


class PFS_l4l():
    def __init__(self, listnew, l4l_sets, vorschaut, display_size):

        from Plugins.Extensions.LCD4linux.module import L4Lelement
        MyElements = L4Lelement()
        #f=open("/tmp/0terms","w")
        #for x in listnew:
        #   f.write(str(x)+"\n")
        #f.close()
        lcd = l4l_sets[0]
        #s1 = MyElements.getResolution(int(lcd))
        s1 = display_size  # MyElements.getResolution(int(lcd))
        screen = l4l_sets[1]
        font = int(l4l_sets[2])
        listnew.sort(key=lambda x: (x[0][0], x[0][1], x[0][2]))
        color = "white"
        color_inactiv = "grey"
        color_ue = "yellow"
        list = []
        ges_list = []
        geblist = []
        termlist = []
        warnlist = []
        filter_list = []
        double_list = []
        datum1 = ""
        t = date.today()
        countdown = 0
        if conf["countdown"]:
            if len(conf["countdown"].split(",")) == 2:
                cd = conf["countdown"].split(",")
                countdown_text = str(cd[0].strip())
                tu = datetime.strptime(str(cd[1]), "%d.%m.%Y")
                cd_date = date(tu.year, tu.month, tu.day) - date.today()
                countdown = cd_date.days
        today = _(_(t.strftime("%A")) + ", " + t.strftime("%d.") + _(t.strftime("%b")) + t.strftime(" %Y"))

        ft = _("HOLIDAY").lower()
        i = 0
        doublet_l = []
        for x in listnew:
            dat = x[3].date()
            alter = 0
            if len(x) > 8:
                dat = x[9].date()
                alter = x[8]
            check = (x[1])
            if conf["doubles"]:
                check = (dat, x[1])
            if check not in doublet_l and dat >= t:
                doublet_l.append(check)
                if i < 20:
                    color1 = "white"
                    color = "white"
                    wt_col = "white"
                    color2 = color
                    alter = x[8]
                    alter2 = ""
                    jutxt = ""
                    jubi = None
                    cat_ind = None
                    categories = (str(x[2]).strip().lower(), str(x[5]).strip().lower())
                    tmp_al = 0
                    zeit = ""
                    jutxt = ""
                    if x[6][0] + x[6][1] > 0:
                        zeit = '%0.2d:%0.2d ' % (x[6][0], x[6][1])
                    wt = wochentage[dat.weekday()]
                    if dat.weekday() == 6:
                        wt_col = "tomato"
                    datum = ' %0.2d' % x[0][2] + "." + '%0.2d' % x[0][1] + "." + " " * 3
                    d_check = datum + x[1] + zeit
                    if datum1 == datum:
                        datum = ""
                        wt = ""
                    else:
                        datum1 = datum
                    such = str(x[1]) + str(x[2]) + str(x[5])
                    if ft in such.lower():
                        jubi = ft
                    else:
                        for tmp in categories1:
                            if tmp.lower().strip() in categories:
                                jubi = tmp
                                cat_ind = categories1.index(tmp)  # +=1
                                break
                            else:
                                if tmp.strip() in such:
                                    jubi = tmp
                                    cat_ind = categories1.index(tmp)
                                    break

                    if jubi:
                        if jubi == ft:
                            if conf["holidays_in_startscreen"] == "Yes":
                                color1 = "tomato"
                                alter2 = ""
                                y = (d_check, zeit + x[1] + alter2, color, 0, "", "", color1, wt_col)
                                if x[4] == 1:
                                    termlist.append(y)
                                else:
                                    y = (d_check, zeit + x[1] + alter2, color, 4, wt, datum, color1, wt_col)
                                    warnlist.append(y)
                            else:
                                datum1 = ""
                                alter2 = ""
                                continue

                        elif cat_ind and z_liste[cat_ind] == "1":
                            alter2 = ""
                            if alter > 0:
                                if alter % 10 == 0:
                                    color1 = "red"
                                elif alter % 5 == 0:
                                    color1 = "red"
                                alter2 = ', ' + str(alter)
                            if jubi.strip() in str(x[1]):
                                alter2 = alter2
                            else:
                                alter2 = ', ' + jubi + alter2  # + ')'

                            if x[4] == 1:
                                y = (d_check, zeit + x[1] + alter2, color1, 0, "", "")
                                if len(alter2):
                                    geblist.append(y)
                                else:
                                    termlist.append(y)
                            else:
                                y = (d_check, zeit + x[1] + alter2, color, 4, wt, datum, color2, wt_col)
                                warnlist.append(y)

                    else:
                        if x[4] == 1:
                            y = (d_check, zeit + x[1], color, 0, "", "", color1, wt_col)
                            termlist.append(y)
                        else:
                            y = (d_check, zeit + x[1], color, 4, wt, datum, color2, wt_col)
                            warnlist.append(y)
                    i += 1
                else:
                    break

#ENDE: fuer Geburts- und Jahrestage, Farbe festlegen und alter bestimmen

        if termlist:
            ges_list.append((3, today, color_ue, 1, ""))
            ges_list.extend(termlist)
        else:
            ges_list.append((4, "-- " + _("No Events registered for today") + " --", color_inactiv, 2, ""))
        if geblist:
            ges_list.append((1, _("Anniversaries today:"), color_ue, 1, ""))
            ges_list.extend(geblist)
        else:
            ges_list.append((2, "-- " + _("No anniversary registered for today") + " --", color_inactiv, 2, ""))

        ges_list.append((5, _("Next events:"), color_ue, 1, ""))
        ges_list.extend(warnlist)

        pos = 0
        ue = 0
        txt_w = None
        txt_file = str(conf["l4l_ges_file"]).lower()
        if txt_file == "on" or txt_file == "yes":
            txt_w = 1
            f = open("/tmp/plfs_ges", "w")

        alg1 = int(font) * 2 + 5  # )#)*3
        for i in range(0, 30):
            MyElements.delete("PLFSlist.01.txt" + str(i))
            MyElements.delete("PLFSlist.02.txt" + str(i))
            MyElements.delete("PLFSlist.03.txt" + str(i))
        i = 0
        MyElements.delete("PLFSlist.05")
        #size=font
        mHight = s1
        if countdown > 0:
            mHight = s1 - ((font + 10) * 2)
        for x in ges_list:
            if i < 20:
                if txt_w:
                    if x[3] == 0 or x[3] == 2:
                        f.write(x[1][0:int(conf["l4l_ges_file_len"])] + "\n")

                if pos < mHight:
                    name = "PLFSlist.01.txt" + str(i)
                    name2 = "PLFSlist.02.txt" + str(i)
                    name3 = "PLFSlist.03.txt" + str(i)
                    size = font

                    alg = 20
                    if x[3] == 0 or x[3] == 4:
                        if ue == 1:
                            pos = pos + 10
                            ue = 0
                        if x[3] == 4:
                            alg = int(font) * 6  # +10 #faktor
                    else:
                        ue = 1
                        size = int(font - font / 6)  # +5
                        pos = pos + 10
                        if x[0] != 1 and x[3] == 1:
                            pos = pos + 10
                        alg = 40
                        if x[3] == 2:
                            alg = 20

                    if x[3] == 4:
                        MyElements.add(name, {"Typ": "txt", "Pos": str(pos), "Text": x[4], "Align": "1%", "Size": str(size), "Color": x[7], "Screen": str(screen), "Lcd": str(lcd), "Mode": "OnMediaIdle"})
                        MyElements.add(name2, {"Typ": "txt", "Align": str(alg1), "Pos": str(pos), "Text": x[5], "Size": str(size), "Color": x[6], "Screen": str(screen), "Lcd": str(lcd), "Mode": "OnMediaIdle"})
                    MyElements.add(name3, {"Typ": "txt", "Align": str(alg), "Pos": str(pos), "Text": x[1], "Size": str(size), "Color": x[2], "Screen": str(screen), "Lcd": str(lcd), "Mode": "OnMediaIdle"})
                    pos = pos + size
                    i += 1
            else:
                break
        if countdown > 0:
            cd_text = countdown_text.replace("pd", str(countdown))  # Sommerurlaub!"
            MyElements.add("PLFSlist.05.txt" + str(i + 2), {"Typ": "txt", "Align": "18%", "Pos": str(pos + 20), "Text": cd_text, "Size": str(size), "Color": x[2], "Screen": str(screen), "Lcd": str(lcd), "Mode": "OnMediaIdle"})

        MyElements.setRefresh()
        if txt_w:
            f.close()


class l4l_export():
    def __init__(self, monate=None):
        from plugin import plfs_list
        new_l = []
        #f=open("/tmp/0l4l","w")
        for x in plfs_list:
            #f.write(str(x)+"\n")
            jubi = 0
            dat = x[3]
            if len(x) > 8:
                jubi = x[8]
                dat = x[9]
            new_l.append((dat, x[1], x[2], x[5], x[6], x[5], jubi))
        self.planerfs_liste = new_l
