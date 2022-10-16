# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext


def localeInit():
    gettext.bindtextdomain("PlanerFS", resolveFilename(SCOPE_PLUGINS, "Extensions/PlanerFS/locale"))


def _(txt):
    t = gettext.dgettext("PlanerFS", txt)
    if t == txt:
        print("[PlanerFS] fallback to default translation for %s" % txt)
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
