#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
import time
from datetime import datetime
import wx
import wx.richtext as rt
import windbreads.utils as wdu

RTC_ALIGNS = dict(default=wx.TEXT_ALIGNMENT_DEFAULT,
                  left=wx.TEXT_ALIGNMENT_LEFT,
                  centre=wx.TEXT_ALIGNMENT_CENTRE,
                  center=wx.TEXT_ALIGNMENT_CENTER,
                  right=wx.TEXT_ALIGNMENT_RIGHT,
                  )


def get_text_width(text, wgt):
    font = wgt.GetFont()
    dc = wx.WindowDC(wgt)
    dc.SetFont(font)
    return dc.GetTextExtent(text)


def get_adjust_size(size=(-1, -1), **kwargs):
    if size == (-1, -1):
        return size

    ratio_size = kwargs.get('ratio_size', (1600, 900))
    w, h = size
    rw, rh = ratio_size
    dw, dh = wx.GetDisplaySize()
    if rw == dw and rh == dh:
        return size

    bw, bh = -1, -1
    if w != -1:
        bw = int((w * dw) / rw)

    if h != -1:
        bh = int((h * dh) / rh)

    return (bw, bh)


def require_int(evt, min_value=1):
    wgt = evt.GetEventObject()
    value = wgt.GetValue().strip()
    if not value.isdigit() or int(value) < min_value:
        wgt.ChangeValue('')
    else:
        wgt.ChangeValue(value)

    wgt.SetInsertionPointEnd()


def pydate2wxdate(date):
    tt = date.timetuple()
    dmy = (tt[2], tt[1] - 1, tt[0])
    return wx.DateTimeFromDMY(*dmy)


def wxdate2pydate(date):
    if date.IsValid():
        return datetime.date(*(map(int, date.FormatISODate().split('-'))))

    return None


def write_echo_text(**kwargs):
    ts_text = kwargs.get('ts_text')
    text = kwargs.get('text', '')
    t = kwargs.get('t')
    if kwargs.get('tff') and t:  # t for file
        text = wdu.ttt(text, t)

    if isinstance(text, unicode):
        text = text.encode('utf-8')

    nl = kwargs.get('nl', True)
    log_mode = kwargs.get('log_mode', 'a')
    for log_file in kwargs.get('log_files', []):
        with open(log_file, log_mode) as f:
            if ts_text:
                f.write(ts_text)

            f.write(text)
            if nl:
                f.write('\n')


def echo_text(rtc, text='', fg=None, bg=None, ts=True, nl=True, italic=False,
              align=None, underline=False, bold=False, ts_style=False,
              font=None, size=None, clear=False, **kwargs):
    t = kwargs.get('t', None)
    ts_text = '[{}] '.format(datetime.now()) if ts else ''
    if isinstance(text, basestring):
        if not isinstance(text, unicode):
            utext = text.decode(wdu.detect_encoding(text)['encoding'])
        else:
            utext = text

    else:
        utext = '{}'.format(text)

    write_echo_text(ts_text=ts_text, text=utext, nl=nl, **kwargs)
    if kwargs.get('no_echo', False):
        if clear:
            rtc.Clear()

        return

    rtc.SetInsertionPointEnd()
    rta = rt.RichTextAttr()
    rta.SetAlignment(RTC_ALIGNS['default'])
    rta.SetTextColour('black')
    rta.SetBackgroundColour('white')
    rta.SetFontStyle(wx.FONTSTYLE_NORMAL)
    rta.SetFontWeight(wx.FONTWEIGHT_NORMAL)
    rta.SetFontUnderlined(False)
    rtc.SetDefaultStyle(rta)
    if ts_text and not ts_style:
        rtc.WriteText(ts_text)

    align = RTC_ALIGNS.get(align)
    if align:
        rta.SetAlignment(align)

    if fg:
        rta.SetTextColour(fg)

    if bg:
        rta.SetBackgroundColour(bg)

    if font:
        rta.SetFontFaceName(font)

    if size:
        rta.SetFontSize(size)

    if bold is True:
        rta.SetFontWeight(wx.FONTWEIGHT_BOLD)
    elif bold is False:
        rta.SetFontWeight(wx.FONTWEIGHT_NORMAL)

    if italic is True:
        rta.SetFontStyle(wx.FONTSTYLE_ITALIC)
    elif italic is False:
        rta.SetFontStyle(wx.FONTSTYLE_NORMAL)

    if underline is not None:
        rta.SetFontUnderlined(underline)

    rtc.BeginStyle(rta)

    if ts_text and ts_style:
        rtc.WriteText(ts_text)

    rtc.WriteText(wdu.ttt(utext, t))
    rtc.EndStyle()
    if nl:
        rtc.Newline()

    rtc.ShowPosition(rtc.GetLastPosition())
    if clear:
        rtc.Clear()


def on_hide(self, evt=None):
    self.Hide()


def on_echoing(self, **kwargs):
    """Default method for echoing text."""
    if self.is_echoing or not self.echo_lines:
        return

    self.is_echoing = True
    while self.echo_lines:
        line = self.echo_lines.pop(0)
        self.echo_text(line[0], **line[1])

    self.is_echoing = False


def start_timer(timer, miliseconds=1000, one_shot=False):
    if timer.IsRunning():
        return

    timer.Start(int(miliseconds), one_shot)


def stop_timer(timer):
    if timer.IsRunning():
        timer.Stop()


def stop_timers(timers=[]):
    [stop_timer(timer) for timer in timers]


def update_clock_statusbar(sbar, ts_fmt='%Y-%b-%d %H:%M', idx=2):
    set_status_text(sbar, time.strftime(ts_fmt), idx)


def set_status_text(sbar, text, idx, t=None):
    sbar.SetStatusText(t(text) if t else text, idx)


def on_popup_lang(self, evt):
    if not hasattr(self, 'english_id'):
        self.english_id = wx.NewId()
        self.chinese_id = wx.NewId()

        self.Bind(wx.EVT_MENU, self.popup_lang, id=self.english_id)
        self.Bind(wx.EVT_MENU, self.popup_lang, id=self.chinese_id)

    menu = wx.Menu()
    menu.Append(self.english_id, 'English', '', wx.ITEM_RADIO)
    menu.Append(self.chinese_id, 'Chinese - 简体中文', '', wx.ITEM_RADIO)
    if self.lang == 'zh':
        menu.Check(self.chinese_id, True)
    else:
        menu.Check(self.english_id, True)

    self.PopupMenu(menu)
    menu.Destroy()


def popup_lang(self, evt):
    lang = 'zh' if evt.GetId() == self.chinese_id else 'en'
    if lang != self.lang:
        self.lang = lang
        self.update_t()
        self.update_ui_lang()
        self.save_lang(lang)

    evt.Skip()


def update_ui_lang(self, refresh=True):
    if hasattr(self, 'lang_wgts'):
        for lwgt in self.lang_wgts:
            tooltip = ''
            if len(lwgt) == 2:
                wgt, label = lwgt
            else:
                wgt, label, tooltip = lwgt

            if tooltip:
                wgt.SetToolTipString(self.tt(tooltip))

            wgt.SetLabel(self.tt(label))

    if refresh:
        if getattr(self, 'panel'):
            self.panel.Layout()

        self.Refresh()
