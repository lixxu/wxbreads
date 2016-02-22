#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
import time
from datetime import datetime
import wx
import wx.richtext as rt

import windbreads.utils as wdu


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


def echo_text(wgt, text='', fg=None, bg=None, ts=True, nl=True, bold=False,
              italic=False, align=None, underline=False, clear=False,
              ts_style=False, font=None, font_size=None, log_file=False,
              **kwargs):
    if clear:
        wgt.Clear()

    t = kwargs.pop('t', None)
    ts_text = '[{}] '.format(datetime.now()) if ts else ''
    utext = '{}'.format(text)

    wgt.SetInsertionPointEnd()
    rta = rt.RichTextAttr()
    rta.SetTextColour('black')
    rta.SetBackgroundColour('white')
    rta.SetFontStyle(wx.FONTSTYLE_NORMAL)
    rta.SetFontWeight(wx.FONTWEIGHT_NORMAL)
    rta.SetFontUnderlined(False)
    wgt.SetDefaultStyle(rta)
    if ts_text and not ts_style:
        wgt.WriteText(ts_text)

    if fg:
        rta.SetTextColour(fg)

    if bg:
        rta.SetBackgroundColour(bg)

    if font:
        rta.SetFontFaceName(font)

    if font_size:
        rta.SetFontSize(font_size)

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

    wgt.BeginStyle(rta)
    if ts_text and ts_style:
        wgt.WriteText(ts_text)

    wgt.WriteText(wdu.ttt(utext, t))
    wgt.EndStyle()
    if nl:
        wgt.Newline()

    wgt.ShowPosition(wgt.GetLastPosition())

    if log_file:
        with open(log_file, 'a') as f:
            if ts_text:
                f.write(ts_text)

            if kwargs.pop('tff') and t:  # t for file
                text = wdu.ttt(utext, t)

            if isinstance(text, unicode):
                text = text.encode('utf-8')

            f.write(text)
            if nl:
                f.write('\n')


def start_timer(timer, miliseconds=1000, one_shot=False):
    if timer.IsRunning():
        return

    timer.Start(int(miliseconds), one_shot)


def stop_timer(timer):
    if timer.IsRunning():
        timer.Stop()


def stop_timers(timers=[]):
    [stop_timer(timer) for timer in timers]


def update_clock_statusbar(sbar, ts_fmt='%d-%b-%Y %H:%M', idx=2):
    set_status_text(sbar, time.strftime(ts_fmt), idx)


def set_status_text(sbar, text, idx, t=None):
    sbar.SetStatusText(t(text) if t else text, idx)


def permission_login(parent=None, root_pass='guess',
                     caption='Security Check',
                     msg='Please enter password:', **kwargs):
    t = kwargs.pop('t', None)
    dlg = wx.PasswordEntryDialog(parent, wdu.ttt(msg, t), wdu.ttt(caption, t))

    # update button labels for i18n
    try:
        std_btn_sizer = dlg.Sizer.GetChildren()[2].Sizer.GetChildren()[1].Sizer
        items = std_btn_sizer.GetChildren()
        ok_btn, cancel_btn = items[1].GetWindow(), items[2].GetWindow()
        ok_btn.SetLabel(wdu.ttt(ok_btn.GetLabel(), t))
        cancel_btn.SetLabel(wdu.ttt(cancel_btn.GetLabel(), t))
    except:
        pass

    size = dlg.GetClientSize()
    dlg.SetMinClientSize(size)
    dlg.SetMaxClientSize(size)
    while 1:
        dlg.SetFocus()
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() == root_pass:
                dlg.Destroy()
                return True

            dlg.SetValue('')
            dlg.SetFocus()
            continue

        dlg.Destroy()
        return False
