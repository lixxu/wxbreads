#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import time
from datetime import datetime
import wx


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


def echo_text(wgt, text='', color=None, clear=False, ts=True, nl=True,
              bold=False, italic=False, align=None, underline=False,
              ts_style=False, log_file=False, **kwargs):
    if clear:
        wgt.Clear()

    t = kwargs.pop('t', None)
    tff = kwargs.pop('tff', None)  # t for file
    wgt.SetInsertionPointEnd()
    ts_text = '[{}] '.format(datetime.now()) if ts else ''
    utext = '{}'.format(text)
    if ts_text and not ts_style:
        wgt.WriteText(ts_text)

    if bold:
        wgt.BeginBold()

    if italic:
        wgt.BeginItalic()

    if underline:
        wgt.BeginUnderline()

    if color:
        wgt.BeginTextColour(color)

    if ts_text and ts_style:
        wgt.WriteText(ts_text)

    wgt.WriteText(tr_text(utext, t))

    if color:
        wgt.EndTextColour()

    if underline:
        wgt.EndUnderline()

    if italic:
        wgt.EndItalic()

    if bold:
        wgt.EndBold()

    if nl:
        wgt.Newline()

    wgt.ShowPosition(wgt.GetLastPosition())

    if log_file:
        with open(log_file, 'a') as f:
            if ts_text:
                f.write(ts_text)

            f.write(tr_text(utext.encode('utf-8'), t if tff else None))
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
    dlg = wx.PasswordEntryDialog(parent, tr_text(msg, t),
                                 tr_text(caption, t))
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
