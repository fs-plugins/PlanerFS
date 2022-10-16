from . import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ConfigList import ConfigListScreen

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Input import Input
from Components.config import getConfigListEntry, ConfigInteger, ConfigYesNo, ConfigClock, ConfigSelection, ConfigNumber, ConfigSequence, config, NoSave

from enigma import eDVBVolumecontrol, eServiceReference, iRecordableService, iPlayableService, eTimer
from time import localtime, mktime
from Components.ServiceEventTracker import ServiceEventTracker


class PFS_show_we(Screen, ConfigListScreen):
    skin = """
		<screen name="Show_Exif" position="center,center" size="310,120" title="Info" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,80" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="155,80" size="140,40"  alphatest="on" />
		<widget name="key_red" position="10,85" zPosition="1" size="140,35" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_green" position="155,85" zPosition="1" size="140,35" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="config" position="5,5" size="300,65" scrollbarMode="showOnDemand" />
		</screen>"""

    def __init__(self, session):

        self.wecker = 0
        self.al_vol_max = 40
        self.now = [x for x in localtime()]
        self.alarm_time = NoSave(ConfigClock(default=mktime(self.now)))
        self.alarm_volume = NoSave(ConfigInteger(default=30, limits=(0, 99)))

        self.sound_on = False

        self.list1 = []
        self.list1.extend((
                        getConfigListEntry(_("alarm time"), self.alarm_time),
                        getConfigListEntry(_("max volume"), self.alarm_volume),
                        ))
        Screen.__init__(self, session)

        self.setTitle(_("alarm-clock") + "   - PlanerFS ")

        #self.loadList()
        ConfigListScreen.__init__(self, self.list1)
        self["key_green"] = Label(_("Start"))
        self["key_red"] = Label(_("Cancel"))

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions", "InfobarChannelSelection"],
            {
             "ok": self.wecker_timer,
             "green": self.wecker_timer,
             "red": self.close,
             "cancel": self.close,
             }, -1)
        self.musicfile = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/PFSsound.mp3"
        self["config"].setList(self.list1)

    def nix(self):
        pass

    def loadList(self):
        self.list1 = []
        self.list1.extend((
                getConfigListEntry(_("alarm time"), self.alarm_time),
                getConfigListEntry(_("max volume"), self.alarm_volume),
                ))

    def wecker_timer(self):
        if self.wecker == 0:
            lt = localtime()
            jetzt = (3600 * lt[3]) + (60 * lt[4]) + lt[5]
            meldezeit = 3600 * self.alarm_time.value[0] + 60 * self.alarm_time.value[1]
            if meldezeit <= jetzt:
                minuszeit = jetzt - meldezeit
                zeitdiff = 86400 - minuszeit
            else:
                zeitdiff = meldezeit - jetzt

            self.session.openWithCallback(self.back, PFS_alarm_clock, self.alarm_volume.value, zeitdiff, None)
            #self.close()

        else:
            pass
            #self.we_timer.stop()

    def back(self, result):
        if result == 0:
            self.close()
        else:
            pass


class PFS_alarm_clock(Screen):
    skin = """
		<screen name="alert" position="center,center" size="250,60" title="alert" flags="wfNoBorder" backgroundColor="transparent">
				<widget name="time" size="250,60" font="Regular;58" foregroundColor="white" valign="center" halign="center" backgroundColor="transparent" />

		</screen>"""

    def __init__(self, session, max_vol=40, zeitdiff=1, DPKG=None):

        self.al_vol_max = max_vol
        self.zeitdiff = zeitdiff
        self.timer1_instanz = False
        self.timer1 = eTimer()
        self.timer1.timeout.get().append(self.klang)

        self.sound_on = False
        self.volctrl = eDVBVolumecontrol.getInstance()

        Screen.__init__(self, session)
        self.setTitle(_("alarm-clock") + "   - PlanerFS ")
        self["time"] = Label(" ")
        self["time"].hide()
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
                                iPlayableService.evEOF: self.__schleife,
                        })

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions", "InfobarChannelSelection"],
            {
             "red": self.exit,
             "cancel": self.exit,
             "ok": self.info,
             "back": self.info,
             "left": self.info,
             "right": self.info,
             "up": self.info,
             "down": self.info,

             }, -1)
        self.musicfile = "/usr/lib/enigma2/python/Plugins/Extensions/PlanerFS/PFSsound.mp3"
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.start_timer)

    def info(self):
        self.session.open(MessageBox, (_("alert-clock is running - press ESC for abort")), MessageBox.TYPE_INFO, timeout=5)

    def start_timer(self):
        self.we_timer = eTimer()
        self.we_timer.callback.append(self.klang)
        self.we_timer.startLongTimer(self.zeitdiff)

    def klang(self):
        self.we_timer = None

        if self.sound_on == False:
            lt = localtime()
            self["time"].setText('%0.2d:%0.2d' % (lt[3], lt[4]))
            self["time"].show()
            oldvol2 = self.volctrl.getVolume()
            if oldvol2 < self.al_vol_max:
                self.volctrl.setVolume(oldvol2 + 1, oldvol2 + 1)
            sref = eServiceReference(4097, 0, self.musicfile)
            self.session.nav.playService(sref)
            self.sound_on = 1

    def __schleife(self):
        self.sound_on = False
        self.session.nav.playService(self.oldService)
        self.timer1.startLongTimer(15)

    def exit(self):
        num = 0
        if self.we_timer:
            self.we_timer.stop()
            num = 1
        if self.sound_on:
            self.session.nav.stopService()
            self.session.nav.playService(self.oldService)
        if self.timer1_instanz:
            self.timer1.stop()
        self.close(num)
