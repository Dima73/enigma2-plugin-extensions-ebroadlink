from . import _

import os
import enigma
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigYesNo, ConfigSelection, NoSave, ConfigIP, ConfigPassword, ConfigText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, HelpableActionMap
from Screens.HelpMenu import HelpableScreen
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap, MultiPixmap

from broadlinkut import ibroadlinkUt, broadlinkUt
import SmartDeviceCommander

# Configuration
config.plugins.broadlink = ConfigSubsection()
config.plugins.broadlink.name = NoSave(ConfigText(default=_("BroadLink"), fixed_size=False))
config.plugins.broadlink.ip = NoSave(ConfigIP(default=[192,168,1,100]))
config.plugins.broadlink.mac = NoSave(ConfigText(default="00:00:00:00:00:00"))
config.plugins.broadlink.system = NoSave(ConfigSelection(default="0", choices=[("0",_("SP2/SP3")),("1",_("RM2")),("3",_("A1")),("2",_("MP1")),("5",_("SP1"))]))
config.plugins.broadlink.user = NoSave(ConfigText(default="administrator", fixed_size=False))
config.plugins.broadlink.passwd = NoSave(ConfigPassword(default="password", fixed_size=False))
config.plugins.broadlink.bqdn = NoSave(ConfigSelection(default="1", choices=[("1",_("Enable power (only SP1/SP2/SP3/MP1)")), ("2",_("Disable power (only SP1/SP2/SP3/MP1)")), ("3",_("Check sensors (only A1)")),("4",_("Check temperature (only RM2)"))]))
config.plugins.broadlink.close = ConfigYesNo(default=False)
cfg = config.plugins.broadlink

class broadlinkEdit(Screen, ConfigListScreen, HelpableScreen):
	skin = """
	<screen position="center,center" size="560,275" title="E-BroadLink Configuration" >

		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget name="config" position="30,40" size="520,200" scrollbarMode="showOnDemand"/>

		<ePixmap pixmap="skin_default/div-h.png" position="0,251" zPosition="1" size="560,2" />
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,258" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="left" position="505,255" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="statusbar" position="10,255" size="470,20" font="Regular;18" />

		<widget name="0" pixmaps="skin_default/buttons/button_green_off.png,skin_default/buttons/button_green.png" position="10,43" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	</screen>"""

	def __init__(self, session, pcinfo=None):
		self.skin = broadlinkEdit.skin
		self.session = session
		self.pcinfo = pcinfo

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self.ip = getConfigListEntry(_("IP"), cfg.ip)
		self.system = getConfigListEntry(_("System"), cfg.system)
		broadlinkEditconfigList = []
		broadlinkEditconfigList.append(getConfigListEntry(_("Name"), cfg.name))
		broadlinkEditconfigList.append(self.system)
		broadlinkEditconfigList.append(self.ip)
		self.mac = getConfigListEntry(_("MAC"), cfg.mac)
		broadlinkEditconfigList.append(self.mac)
		#broadlinkEditconfigList.append(getConfigListEntry(_("User"),cfg.user))
		#broadlinkEditconfigList.append(getConfigListEntry(_("Password"), cfg.passwd))
		broadlinkEditconfigList.append(getConfigListEntry(_("BouqDown"), cfg.bqdn))
		broadlinkEditconfigList.append(getConfigListEntry(_("Closing plugin (BouqDown/BouqUp)"), cfg.close))

		ConfigListScreen.__init__(self, broadlinkEditconfigList, session=self.session, on_change=self.changedEntry)

		if self.pcinfo is None:
			self.pcinfo = {'name': False, 'ip': False, 'mac': False, 'system': False, 'user': False, 'passwd': False, 'bqdn': False}

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Ok"))
		self["key_yellow"] = Button(_("Overview broadlink devices"))
		self["key_blue"] = Button(_("Get MAC"))

		self["statusbar"] = Label()
#		self["statusbar"].setText(_("BouqUp for WakeUp"))

		self["0"] = MultiPixmap()

		self.remotepc = {}

		self["broadlinkActions"] = HelpableActionMap(self, "broadlinkActions",
			{
			"ok": self.ok,
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.ok,
			"yellow": (self.getNetworkOverview, _("Network overview broadlink devices")),
			"blue": (self.getDeviceMAC, _("Get MAC of running device")),
			}, -1)
		self.setup_title = _("E-BroadLink: %s" % (self.pcinfo['name']))
		self.onChangedEntry = []
		self.remotepc = ibroadlinkUt.getPCsList()
		self.fillCfg()
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.isAlive)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def setWindowTitle(self):
		self.setTitle(_("E-BroadLink configuration:") + " " + "%s" % (self.pcinfo['name']))

	def getNetworkOverview(self):
		import SmartDeviceCommander
		devices = SmartDeviceCommander.discover(timeout=5)
		menu = []
		if devices:
			print len(devices)
			for dev in devices:
				name = "%s - %s" % (dev.type, dev.host)
				menu.append((name, dev))
			def brction(choice):
				if choice:
					str_type = choice[1].type
					if str_type == "Unknown":
						self.session.open(MessageBox, _("Not apply!\nBroadLink device type is unknown!"), type=MessageBox.TYPE_ERROR, timeout=5)
						return
					if str_type == "MP1":
						cfg.system.value = "2"
					elif str_type == "SP2/SP3":
						cfg.system.value = "0"
					elif str_type == "RM2":
						cfg.system.value = "1"
					elif str_type == "A1":
						cfg.system.value = "3"
					elif str_type == "SP1":
						cfg.system.value = "5"
					prev_ip = cfg.ip.value
					host = choice[1].host
					try:
						cfg.ip.value = self.convertIP(host[0])
						ip = "%s.%s.%s.%s" % (tuple(cfg.ip.value))
					except:
						cfg.ip.value = prev_ip
					if prev_ip != cfg.ip.value:
						self.getDeviceMAC()
					self["config"].invalidate(self.system)
					self["config"].invalidate(self.ip)
			self.session.openWithCallback(brction, ChoiceBox, title=_("Select device for use:"), list=menu)

	def getDeviceMAC(self):
		ip = "%s.%s.%s.%s" % (tuple(cfg.ip.value))
		self.readAlive(ip)
		pcMAC = self.readMac(ip)
		if pcMAC is not None:
			cfg.mac.value = pcMAC
			self["config"].invalidate(self.mac)
		else:
			res = os.system("ping -c 2 -W 1 %s >/dev/null 2>&1" % (ip))
			if not res:
				pcMAC = self.readMac(ip)
				if pcMAC is not None:
					cfg.mac.value = pcMAC
					self["config"].invalidate(self.mac)

	def readMac(self, ip):
		pcMAC = None
		file = open("/proc/net/arp", "r")
		while True:
			entry = file.readline().strip()
			if entry == "":
				break
			if entry.find(ip) == 0:
				p = entry.find(':')
				pcMAC = entry[p - 2:p + 15]
				if pcMAC != "00:00:00:00:00:00":
					file.close()
					return pcMAC
		file.close()
		return None

	def isAlive(self):
		ip = "%s.%s.%s.%s" % (tuple(cfg.ip.value))
		self.readAlive(ip)

	def readAlive(self,ip):
		res = os.system("ping -c 1 -W 1 %s >/dev/null 2>&1" % (ip))
		if not res:
			self["0"].setPixmapNum(1)
			return True
		else:
			self["0"].setPixmapNum(0)
		return False

	def fillCfg(self):
		if self.pcinfo.has_key('name'):
			cfg.name.value = self.pcinfo['name']
		if self.pcinfo.has_key('ip'):
			cfg.ip.value = self.convertIP(self.pcinfo['ip'])
		if self.pcinfo.has_key('mac'):
			cfg.mac.value = self.pcinfo['mac']
		if self.pcinfo.has_key('system'):
			cfg.system.value = self.pcinfo['system']
		if self.pcinfo.has_key('user'):
			cfg.user.value = self.pcinfo['user']
		if self.pcinfo.has_key('passwd'):
			cfg.passwd.value = self.pcinfo['passwd']
		if self.pcinfo.has_key('bqdn'):
			cfg.bqdn.value = self.pcinfo['bqdn']

	def convertIP(self, ip):
		strIP = ip.split('.')
		ip = []
		for x in strIP:
			ip.append(int(x))
		return ip

	def ok(self):
		current = self["config"].getCurrent()
		name = cfg.name.value
		if self.remotepc.has_key(name) is True:
			self.session.openWithCallback(self.updateConfig, MessageBox, (_("A BroadLink entry with this name already exists!\nUpdate existing entry and continue?")))
		else:
			self.session.openWithCallback(self.applyConfig, MessageBox, (_("Are you sure you want to add this BroadLink smart?\n")))

	def updateConfig(self, ret=False):
		if (ret == True):
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "name", cfg.name.value)
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "ip", cfg.ip.getText())
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "mac", cfg.mac.value)
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "system", cfg.system.value)
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "user", cfg.user.value)
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "passwd", cfg.passwd.value)
			ibroadlinkUt.setRemotePCAttribute(cfg.name.value, "bqdn", cfg.bqdn.value)

			self.session.openWithCallback(self.updateFinished, MessageBox, _("Your BroadLink has been updated..."), type=MessageBox.TYPE_INFO, timeout=2)
			ibroadlinkUt.writePCsConfig()
			cfg.close.save()
			ibroadlinkUt.configActualized = True
		else:
			self.close()

	def updateFinished(self,data):
		if data is not None and data is True:
			self.close()

	def applyConfig(self, ret=False):
		if (ret == True):
			data = {'name': False, 'ip': False, 'mac': False, 'system': False, 'username': False, 'password': False, 'bqdn': False}
			data['name'] = cfg.name.value
			data['ip'] = cfg.ip.getText()
			data['mac'] = cfg.mac.value
			data['system'] = cfg.system.value
			data['user'] = cfg.user.value
			data['passwd'] = cfg.passwd.value
			data['bqdn'] = cfg.bqdn.value

			self.session.openWithCallback(self.applyFinished, MessageBox, _("Your new BroadLink smart has been added."), type=MessageBox.TYPE_INFO, timeout=2)
			ibroadlinkUt.remotepc[cfg.name.value] = data
			ibroadlinkUt.writePCsConfig()
			ibroadlinkUt.configActualized = True
		else:
			self.close()

	def applyFinished(self, data):
		if data is not None and data is True:
			self.close()

	def cancel(self):
		self.close()
