import urwid

class Select(urwid.WidgetWrap):

	def __init__(self, desc, choices):
		self.options = []
		self.status = urwid.Text("None")
		widgets = []
		for txt, val, sel in choices:
			if sel:
				self.status.set_text(val)
			b = urwid.RadioButton(self.options, txt, sel, self.on_change, val)
			widgets.append( b )

		wlist = urwid.Filler(urwid.Pile(widgets), "top")
		dispw = urwid.Frame(wlist, urwid.Text(desc, "center"), self.status)
		box = urwid.LineBox(dispw)
		urwid.WidgetWrap.__init__(self, box)

	def on_change(self, button, state, data):
		if state:
			self.status.set_text(data)

	def getValue(self):
		return self.status.get_text()[0]


class BaseWindow(urwid.WidgetWrap):

	def __init__(self, widget):
		frame = urwid.Frame(widget, urwid.AttrMap(urwid.Text("KGP installer","center"),"banner"))

		urwid.WidgetWrap.__init__(self, frame)


class BaseWizard(BaseWindow):

	def __init__(self,mainwidget,nxtlbl="Next", prvlbl="Prev", nxtcallback=None, prvcallback=None):

		self.nextcallback = nxtcallback
		self.prevcallback = prvcallback

		nxt = urwid.Filler(urwid.Padding(urwid.Button(nxtlbl, self._next), "center", "pack"))
		prev = urwid.Filler(urwid.Padding(urwid.Button(prvlbl, self._prev), "center", "pack"))

		control = urwid.Columns([prev, nxt], focus_column = 1)
		content = urwid.Pile([mainwidget, control], 1)

		BaseWindow.__init__(self, content)
	
	def _next(self, button):
		if self.nextcallback:
			self.nextcallback()	

	def _prev(self, button):
		if self.prevcallback:
			self.prevcallback()	

class SelectWindow(BaseWizard):


	def __init__(self, netifs, disks, ok, cancel):
		self.netsel = Select("Network interface", netifs )
		self.storsel = Select("Storage device", disks)
		
		qs = [ self.netsel, self.storsel ] 
	
		cols = urwid.Columns(qs)
		
		BaseWizard.__init__(self, cols, "Next", "Cancel", ok, cancel)


	def getDisk(self):
		return self.storsel.getValue()

	def getNetif(self):
		return self.netsel.getValue()


class StartWindow(BaseWizard):

	def __init__(self, start, back):
	
		slabel = urwid.Filler(urwid.Text("Storage device: ","right"))
		nlabel = urwid.Filler(urwid.Text("Network device: ","right"))
		
		self.netif = urwid.Text("N/A")
		self.disk = urwid.Text("N/A")

		netif = urwid.Filler(self.netif)
		disk = urwid.Filler(self.disk)

		diskc = urwid.Columns([slabel, disk])
		netc = urwid.Columns([nlabel, netif])
		#content = urwid.Pile([urwid.Filler(urwid.Padding(self.text,"center","pack"))])
		content = urwid.Pile([diskc, netc])

		BaseWizard.__init__(self, content, "Start install", "Back", start, back)


	def update(self, disk, netif):
		self.netif.set_text(netif)
		self.disk.set_text(disk)
