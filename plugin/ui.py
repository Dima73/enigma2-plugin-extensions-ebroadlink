# for localized messages
from . import _

from Screens.Screen import Screen
from Components.Sources.List import List
from Components.ActionMap import ActionMap, HelpableActionMap
from Screens.HelpMenu import HelpableScreen
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.Label import Label
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from enigma import eTimer
import os

from broadlinkut import ibroadlinkUt, broadlinkUt
from broadlinkedit import broadlinkEdit
import SmartDeviceCommander

version = "1.2"

SP2SP3 = "0"
RM2 = "1"
MP1 = "2"
SP1 = "5"
A1 = "3"

ENABLEPOWER = "1"
DISABLEPOWER = "2"
CHECKSENSORS = "3"
CHECKTEMPERATURE = "4"

class broadlinkSummary(Screen):
	skin = """
	<screen position="0,0" size="96,64">
		<widget source="title" render="Label" position="0,0" size="96,12" font="FdLcD;12" halign="left" foregroundColor="#00ccc040" />
		<widget source="pcname" render="Label" position="0,12" size="200,40" font="FdLcD;40" halign="left" valign="center" foregroundColor="#00f0f0f0"/>
		<widget source="bouquet" render="Label" position="0,52" size="96,12" font="FdLcD;12" halign="left" foregroundColor="#00ccc040"/>
	</screen>"""

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["title"] = StaticText(_(parent.setup_title))
		self["pcname"] = StaticText("")
		self["bouquet"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)
		self.parent["config"].onSelectionChanged.remove(self.selectionChanged)

	def selectionChanged(self):
		self["pcname"].text = self.parent.getCurrentEntry()
		self["bouquet"].text = self.parent.getCurrentValue()

class broadlink(Screen, HelpableScreen):
	skin = """
	<screen position="center,center" size="560,430" title="E-BroadLink" >

		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget source="config" render="Listbox" position="10,50" size="545,360" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryPixmapAlphaTest(pos = (15, 5), size = (50, 40), png = 0), # index 0 is the E-BroadLink pixmap (for pixmap it is png= )
						MultiContentEntryText(pos = (90, 6), size = (120, 45), font=0, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the Name (for text it is text= )
						MultiContentEntryPixmapAlphaTest(pos = (220, 5), size = (50, 40), png = 2), # index 2 is the system pixmap
						MultiContentEntryText(pos = (290, 3), size = (250, 20), font=1, flags = RT_HALIGN_LEFT, text = 3), # index 3 is the IP
						MultiContentEntryText(pos = (290, 23), size = (250, 20), font=1, flags = RT_HALIGN_LEFT, text = 4), # index 4 is the MAC
						],
					"fonts": [gFont("Regular", 22),gFont("Regular", 18)],
					"itemHeight": 50
				}
			</convert>
		</widget>

		<ePixmap pixmap="skin_default/div-h.png" position="0,406" zPosition="1" size="560,2" />
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,413" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="left" position="505,410" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<ePixmap pixmap="skin_default/buttons/key_menu.png" position="430,408" zPosition="3" size="35,25" alphatest="on" transparent="1" />
		<widget name="statusbar" position="0,410" size="430,20" font="Regular;17" />

	</screen>"""

	def __init__(self, session, plugin_path):
		self.skin = broadlink.skin
		self.session = session
		self.ppath = plugin_path
		self.setup_title = _("E-BroadLink")

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Add/Edit"))
		self["key_yellow"] = Button(_("Delete"))
		self["key_blue"] = Button(_("Overview broadlink devices"))

		self.list = []

		self["config"] = List(self.list)
		self["statusbar"] = Label()
		self.text = _("User defined...")
		self.text1 = "..."

		self["broadlinkActions"] = HelpableActionMap(self, "broadlinkActions",
			{
			"red": (self.cancel, _("Close plugin")),
			"green": (self.keyOK, _("Add/Edit item")),
			"yellow": (self.deleteItem, _("Delete selected item")),
			"blue": (self.getNetworkOverview, _("Overview broadlink devices")),
			"bouqdn": (self.bouqDown, self.text),
			"cancel": (self.cancel, _("Close plugin")),
			"ok": (self.keyOK, _("Add/Edit item")),
			"menu": (self.showMenu, _("Select option")),
			"bouqup": (self.bouqUp, self.text1),
			}, -1)

		self.ipStr = _("IP:")+" "
		self.macStr = _("MAC:")+" "

		self.pcinfo = None
		self.closing = False
		self.showPCsList()

		self.commandTimer = eTimer()
		self.commandTimer.timeout.get().append(self.sendDelayed)

		self.onShown.append(self.prepare)
		self["config"].onSelectionChanged.append(self.statusbarText)

		self.onChangedEntry = []

	def getCurrentEntry(self):
		current = self["config"].getCurrent()
		return ibroadlinkUt.remotepc[current[1]]['name']

	def getCurrentValue(self):
		self.statusbarText()
		return _("BouqDn: %s") % (self.text)

	def createSummary(self):
		return broadlinkSummary

	def prepare(self):
		self.setTitle(_("E-BroadLink") + " " + version)

	def getNetworkOverview(self):
		devices = SmartDeviceCommander.discover(timeout=5)
		if devices:
			menu = []
			for dev in devices:
				menu.append((_("%s - %s") % (dev.type, dev.host), dev))
			def brction(choice):
				pass
			self.session.openWithCallback(brction, ChoiceBox, title=_("Network overview BroadLink devices..."), list=menu)

	def showMenu(self):
		self.command = ""
		self.closing = False
		if self.pcinfo is None: return
		menu_title_text = "%s" % (self.pcinfo['name']) + _(" - select action:")
		menu = []
		if self.pcinfo['system'] == SP2SP3 or self.pcinfo['system'] == SP1 or self.pcinfo['system'] == MP1:
			if self.pcinfo['system'] != SP1:
				menu.append((_("Status power"),"statuspower"))
			if self.pcinfo['system'] == SP2SP3 or self.pcinfo['system'] == SP1:
				menu.append((_("Enable power"),"enablepower"))
				menu.append((_("Disable power"),"disablepower"))
				if self.pcinfo['system'] == SP2SP3:
					menu.append((_("Current energy only SP2/SP3S"),"energymonitor"))
			elif self.pcinfo['system'] == MP1:
				menu.append((_("Enable power (socket 1)"),"enablepower1"))
				menu.append((_("Enable power (socket 2)"),"enablepower2"))
				menu.append((_("Enable power (socket 3)"),"enablepower3"))
				menu.append((_("Enable power (socket 4)"),"enablepower4"))
				menu.append((_("Disable power (socket 1)"),"disablepower1"))
				menu.append((_("Disable power (socket 2)"),"disablepower2"))
				menu.append((_("Disable power (socket 3)"),"disablepower3"))
				menu.append((_("Disable power (socket 4)"),"disablepower4"))
		if self.pcinfo['system'] == A1:
			menu.append((_("Check sensors"),"sensor"))
		if self.pcinfo['system'] == RM2:
			menu.append((_("Check temperature"),"temperature"))
		if menu:
			def subMenu(choice):
				if choice is None:
					return
				self.command = choice[1]
				self.sendCommand()
			self.session.openWithCallback(subMenu, ChoiceBox, title = menu_title_text, list=menu)

	def statusbarText(self):
		self.text = _("User defined...")
		current = self["config"].getCurrent()
		if current:
			self.pcinfo = ibroadlinkUt.remotepc[current[1]]
			if self.pcinfo is None: return
			soccet_type = False 
			if self.pcinfo['system'] == SP2SP3 or self.pcinfo['system'] == SP1 or self.pcinfo['system'] == MP1:
				if self.pcinfo['system'] != SP1:
					self.text1 = _("Status power")
				soccet_type = True
			if self.pcinfo['bqdn'] == ENABLEPOWER:
				self.text = soccet_type and _("Enable power") or "..."
			if self.pcinfo['bqdn'] == DISABLEPOWER:
				self.text = soccet_type and _("Disable power") or "..."
			if self.pcinfo['bqdn'] == CHECKSENSORS:
				self.text = self.pcinfo['system'] == A1 and _("Check sensors")or "..."
			if self.pcinfo['bqdn'] == CHECKTEMPERATURE:
				self.text = self.pcinfo['system'] == RM2 and _("Check temperature") or "..."
		self["statusbar"].setText(_("BouqUp for %s, BouqDn for %s") % (self.text1, self.text))

	def bouqDown(self):
		self.command = ""
		if self.pcinfo is None: return
		if self.pcinfo['bqdn'] == ENABLEPOWER:
			if self.pcinfo['system'] == SP2SP3 or self.pcinfo['system'] == SP1:
				self.closing = True
				self.command = "enablepower"
				self.sendDelayed()
			elif self.pcinfo['system'] == MP1:
				self.closing = True
				self.command = "enablepowerall"
				self.sendDelayed()
			else:
				self.message(_("Command not support %s.") % (self.pcinfo['name']),5,"error")
		if self.pcinfo['bqdn'] == DISABLEPOWER:
			if self.pcinfo['system'] == SP2SP3 or self.pcinfo['system'] == SP1:
				self.closing = True
				self.command = "disablepower"
				self.sendDelayed()
			elif self.pcinfo['system'] == MP1:
				self.closing = True
				self.command = "disablepowerall"
				self.sendDelayed()
			else:
				self.message(_("Command not support %s.") % (self.pcinfo['name']),5,"error")
		if self.pcinfo['bqdn'] == CHECKSENSORS:
			if self.pcinfo['system'] == A1:
				self.closing = True
				self.command = "sensor"
				self.sendDelayed()
			else:
				self.message(_("Command not support %s.") % (self.pcinfo['name']),5,"error")
		if self.pcinfo['bqdn'] == CHECKTEMPERATURE:
			if self.pcinfo['system'] == RM2:
				self.closing = True
				self.command = "temperature"
				self.sendDelayed()
			else:
				self.message(_("Command not support %s.") % (self.pcinfo['name']),5,"error")

	def bouqUp(self):
		self.command = ""
		if self.pcinfo is None: return
		if self.pcinfo['system'] == SP2SP3 or self.pcinfo['system'] == MP1:
			self.closing = True
			self.command = "statuspower"
			self.sendDelayed()
		else:
			self.message(_("Command not support %s.") % (self.pcinfo['name']),5,"error")

	def getItemParams(self, pcinfo):
		ip = pcinfo['ip']
		user = pcinfo['user']
		passwd = pcinfo['passwd']
		os = pcinfo['system']
		mac = pcinfo['mac']
		return (os, ip, user, passwd, mac)

	def isAlive(self):
		if self.alive():
			return True
		else:
			self.message(_("No response from %s.") % (self.pcinfo['name']), 5, "error")
			return False

	def sendCommand(self):
		if self.isAlive():
			self.commandTimer.start(100, True)

	def exitPlugin(self, data):
		if data is not None and data:
			if config.plugins.broadlink.close.value and self.closing:
				self.close()

	def sendDelayed(self):
		self.commandTimer.stop()
		if self.pcinfo is None: return
		mac_str = str(self.pcinfo["mac"]).replace(":", "")
		mac_str = mac_str.upper()
		mac = mac_str.decode('hex')
		ip = str(self.pcinfo['ip'])
		device = None
		if self.pcinfo['system'] == SP2SP3:
			try:
				device = SmartDeviceCommander.sp2((ip, 80),mac)
			except:
				pass
		elif self.pcinfo['system'] == SP1:
			try:
				device = SmartDeviceCommander.sp1((ip, 80),mac)
			except:
				pass
		elif self.pcinfo['system'] == MP1:
			try:
				device = SmartDeviceCommander.mp1((ip, 80),mac)
			except:
				pass
		elif self.pcinfo['system'] == A1:
			try:
				device = SmartDeviceCommander.a1((ip, 80),mac)
			except:
				pass
		elif self.pcinfo['system'] == RM2:
			try:
				device = SmartDeviceCommander.rm((ip, 80),mac)
			except:
				pass
		if device is None or not device.auth():
			self.session.openWithCallback(self.exitPlugin, MessageBox,_("Unknown error!\n"),type = MessageBox.TYPE_ERROR, timeout = 5)
			return
		add = ""
		text = ""
		if self.command == "statuspower":
			status = device.check_power()
			if self.pcinfo['system'] == MP1:
				if status is not None:
					sp1 = status.get("sp1", None)
					if sp1 == False:
						add = _(": socket 1 disabled")
					elif sp1 == True:
						add = _(": socket 1 enabled")
					else:
						add = _(": socket 1 state unknown")
					text += _("Power status") + add
					sp2 = status.get("sp2", None)
					if sp2 == False:
						add = _(": socket 2 disabled")
					elif sp2 == True:
						add = _(": socket 2 enabled")
					else:
						add = _(": socket 2 state unknown")
					text += "\n" + _("Power status") + add
					sp3 = status.get("sp3", None)
					if sp3 == False:
						add = _(": socket 3 disabled")
					elif sp3 == True:
						add = _(": socket 3 enabled")
					else:
						add = _(": socket 3 state unknown")
					text += "\n" + _("Power status") + add
					sp4 = status.get("sp4", None)
					if sp4 == False:
						add = _(": socket 4 disabled")
					elif sp4 == True:
						add = _(": socket 4 enabled")
					else:
						add = _(": socket 4 state unknown")
					text += "\n" + _("Power status") + add
			else:
				if status == False:
					add = _(": socket disabled")
				elif status == True:
					add = _(": socket enabled")
				else:
					add = _(": socket state unknown")
				text = _("Power status") + add
		elif self.command == "enablepower":
			text = _("Enable power") + "!"
			device.set_power(True)
		elif self.command == "disablepower":
			text = _("Disable power") + "!"
			device.set_power(False)
		elif self.command == "enablepower":
			text = _("Enable power") + "!"
			device.set_power(True)
		elif self.command == "disablepower":
			text = _("Disable power") + "!"
			device.set_power(False)
		elif self.command == "enablepowerall":
			text = _("Enable power") + _("( all socket)") + "!"
			device.set_power(1, True)
			device.set_power(2, True)
			device.set_power(3, True)
			device.set_power(4, True)
		elif self.command == "enablepower1":
			text = _("Enable power (socket 1)") + "!"
			device.set_power(1, True)
		elif self.command == "enablepower2":
			text = _("Enable power (socket 2)") + "!"
			device.set_power(2, True)
		elif self.command == "enablepower3":
			text = _("Enable power (socket 3)") + "!"
			device.set_power(3, True)
		elif self.command == "enablepower4":
			text = _("Enable power (socket 4)") + "!"
			device.set_power(4, True)
		elif self.command == "disablepowerall":
			text = _("Disable power") + _("( all socket)") + "!"
			device.set_power(1, False)
			device.set_power(2, False)
			device.set_power(3, False)
			device.set_power(4, False)
		elif self.command == "disablepower1":
			text = _("Disable power (socket 1)") + "!"
			device.set_power(1, False)
		elif self.command == "disablepower2":
			text = _("Disable power (socket 2)") + "!"
			device.set_power(2, False)
		elif self.command == "disablepower3":
			text = _("Disable power (socket 3)") + "!"
			device.set_power(3, False)
		elif self.command == "disablepower4":
			text = _("Disable power (socket 4)") + "!"
			device.set_power(4, False)
		elif self.command == "sensor":
			status = device.check_sensors()
			if status:
				temperature = status.get("temperature", "")
				if temperature:
					text += _("Temperature") + ": " + str(temperature) + " C"
					text += "\n"
				humidity = status.get("humidity", "")
				if humidity:
					text += _("Humidity") + ": " + str(humidity)
					text += "\n"
				light = status.get("light", "")
				if light:
					text += _("Light") + ": " + light
					text += "\n"
				air_quality = status.get("air_quality", "")
				if air_quality:
					text += _("Air quality") + ": " + air_quality
					text += "\n"
				noise = status.get("noise", "")
				if noise:
					text += _("Noise") + ": " + noise
					text += "\n"
		elif self.command == "temperature":
			status = device.check_temperature()
			text =_("Temperature") + ": " + str(status) + " C"
		elif self.command == "energymonitor":
			#if device.devtype == 0x9479 or device.devtype == 0x947a or device.devtype == 0x2711 or device.devtype == 0x2719 or device.devtype == 0x7919 or device.devtype == 0x271a or device.devtype == 0x791a:
			status = device.get_energy()
			if status is None:
				extra_text = _("unknown")
			else:
				extra_text = str(status) + " W"
			text =_("Current energy") + ": " + extra_text
			#else:
			#	text = _("Command not support!")
		self.session.openWithCallback(self.exitPlugin, MessageBox,_("Device %s\n\n%s\n") % (self.pcinfo['name'], text),type = MessageBox.TYPE_INFO, timeout = 6)

	def showPCsList(self):
		oldIndex = self["config"].getIndex()
		oldCount = self["config"].count()
		list = []
		remotepc = ibroadlinkUt.getPCsList()
		for name in remotepc.keys():
			list.append(self.buildPCViewItem(ibroadlinkUt.remotepc[name]))
		list.sort(key = lambda x: x[1])
		self["config"].setList(list)
		newCount = self["config"].count()
		newIndex = self["config"].getIndex()
		self.setListIndex(oldIndex, newIndex, oldCount, newCount)

	def setListIndex(self, oldIndex, newIndex, oldCount, newCount):
		if newIndex != None: 
			if oldIndex + 1 == oldCount:
				if oldCount < newCount:
					self["config"].setIndex(oldIndex+1)
				elif oldCount > newCount:
					self["config"].setIndex(oldIndex-1)
				else:
					self["config"].setIndex(oldIndex)
			else:
				self["config"].setIndex(oldIndex)

	def buildPCViewItem(self, entry):
		pc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/device.png"))
		logo = pc
		ip = "".join((self.ipStr,str(entry["ip"])))
		mac = "".join((self.macStr,str(entry["mac"])))
		system = entry["system"]
		if system == RM2:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/rm2.png"))
		elif system == A1:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/a1.png"))
		elif system == MP1:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/mp1.png"))
		elif system == SP1:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/sp1.png"))
		elif system == SP2SP3:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/sp23.png"))
		return( pc, entry["name"], logo, ip, mac )

	def keyOK(self):
		self.session.openWithCallback(self.editClosed, broadlinkEdit, self.pcinfo)

	def editClosed(self):
		if ibroadlinkUt.configActualized:
			self.showPCsList()

	def deleteItem(self):
		self.retValue = self.pcinfo['name']
		self.session.openWithCallback(self.removeData, MessageBox, _("Do You want remove BroadLink device: %s?") % (self.pcinfo['name']), type = MessageBox.TYPE_YESNO)

	def removeData(self, answer=None):
		if answer is not None and answer:
			ibroadlinkUt.removePC(self.retValue)
			ibroadlinkUt.writePCsConfig()
			ibroadlinkUt.getRemotePCPoints()
			self.showPCsList()
			self.session.open(MessageBox, _("BroadLink device has been removed..."), type = MessageBox.TYPE_INFO, timeout = 3)

	def message(self, string, delay, msg_type=""):
		msg = MessageBox.TYPE_INFO
		if msg_type=="error":
			msg = MessageBox.TYPE_ERROR
		self.session.open(MessageBox, string, type = msg, timeout = delay)

	def cancel(self):
		self.close()

	def getHostname(self):
		hostname = "enigma2"
		if os.path.exists("/etc/hostname"):
			fp = open('/etc/hostname', 'r')
			if fp:
				hostname = fp.readline()[:-1]
				fp.close()
		return hostname

	def alive(self):
		if not os.system("ping -c 2 -W 1 %s >/dev/null 2>&1" % (self.pcinfo['ip'])):
			return True
		return False

	def GetIPsFromNetworkInterfaces(self):
		import socket, fcntl, struct, array, sys
		is_64bits = sys.maxsize > 2**32
		struct_size = 40 if is_64bits else 32
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		max_possible = 8 # initial value
		while True:
			_bytes = max_possible * struct_size
			names = array.array('B')
			for i in range(0, _bytes):
				names.append(0)
			outbytes = struct.unpack('iL', fcntl.ioctl(
				s.fileno(),
				0x8912,  # SIOCGIFCONF
				struct.pack('iL', _bytes, names.buffer_info()[0])
			))[0]
			if outbytes == _bytes:
				max_possible *= 2
			else:
				break
		namestr = names.tostring()
		ifaces = []
		for i in range(0, outbytes, struct_size):
			iface_name = bytes.decode(namestr[i:i+16]).split('\0', 1)[0].encode('ascii')
			if iface_name != 'lo':
				iface_addr = socket.inet_ntoa(namestr[i+20:i+24])
				ifaces.append((iface_name, iface_addr))
		return ifaces
