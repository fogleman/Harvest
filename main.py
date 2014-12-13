import model
import time
import wx

class View(wx.Panel):
    def __init__(self, parent):
        super(View, self).__init__(parent)
        self.model = model.Model()
        self.hover = (0, 0)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.timestamp = time.time()
        self.on_timer()
    def on_timer(self):
        t = time.time()
        dt = t - self.timestamp
        self.timestamp = t
        self.model.update(t, dt)
        self.Refresh()
        wx.CallLater(10, self.on_timer)
    def on_motion(self, event):
        sx, sy = event.GetPosition()
        x, y = self.to_grid(sx, sy)
        if self.model.grid.inside((x, y)):
            self.hover = (x, y)
    def on_left_down(self, event):
        sx, sy = event.GetPosition()
        x, y = self.to_grid(sx, sy)
        self.model.grid.toggle_wall((x, y))
        self.Refresh()
    def on_right_down(self, event):
        self.model.reset()
        self.Refresh()
    def on_size(self, event):
        event.Skip()
        self.Refresh()
    def on_paint(self, event):
        self.metrics = self.compute_metrics()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        self.draw(dc)
    def compute_metrics(self):
        grid = self.model.grid
        pad = 20
        cw, ch = self.GetClientSize()
        gw, gh = grid.size
        sx = (cw - pad * 2) / gw
        sy = (ch - pad * 2) / gh
        size = min(sx, sy)
        dx = (cw - size * gw) / 2
        dy = (ch - size * gh) / 2
        return (size, dx, dy)
    def to_screen(self, x, y):
        size, dx, dy = self.metrics
        sx = dx + x * size
        sy = dy + y * size
        return (sx, sy)
    def to_grid(self, sx, sy):
        size, dx, dy = self.metrics
        x = (sx - dx) / size
        y = (sy - dy) / size
        return (x, y)
    def draw(self, dc):
        self.draw_grid(dc)
        self.draw_bots(dc)
    def draw_grid(self, dc):
        grid = self.model.grid
        size = self.metrics[0]
        for y in range(grid.height):
            for x in range(grid.width):
                sx, sy = self.to_screen(x, y)
                if grid.has_wall((x, y)):
                    dc.SetPen(wx.BLACK_PEN)
                    dc.SetBrush(wx.BLACK_BRUSH)
                else:
                    dc.SetPen(wx.Pen(wx.Colour(221, 221, 221)))
                    dc.SetBrush(wx.WHITE_BRUSH)
                dc.DrawRectangle(sx, sy, size + 1, size + 1)
                # d = grid.get_distance(self.hover, (x, y))
                # dc.DrawText(str(d), sx + 5, sy + 5)
    def draw_bots(self, dc):
        size = self.metrics[0]
        dc.SetBrush(wx.RED_BRUSH)
        dc.SetPen(wx.TRANSPARENT_PEN)
        for bot in self.model.bots:
            sx, sy = self.to_screen(*bot.position)
            dc.DrawCircle(sx + size / 2, sy + size / 2, size / 8)
            # sx, sy = self.to_screen(*bot.target)
            # dc.DrawCircle(sx + size / 2, sy + size / 2, size / 16)

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Harvest')
        self.SetClientSize((600, 600))
        self.view = View(self)

def main():
    app = wx.App()
    frame = Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
