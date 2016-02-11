#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import wx
from pyldaplite import ldap, PyLDAPLite
import utils

HIGHLIGHT_RED = '#F75D59'


def ldap_login(server, base_dn, login_name, password, close=True):
    p = PyLDAPLite(server=server, base_dn=base_dn)
    try:
        p.connect(login_name, password)
    except ldap.SERVER_DOWN as e:
        return 100, e
    except ldap.INVALID_CREDENTIALS:
        return 200, None
    except:
        return 300, sys.exc_info()[0]
    else:
        if close:
            p.close()
        else:
            return 0, p

    return 0, None


class LoginWindow(wx.Dialog):
    def __init__(self, parent=None, title='User Login',
                 size=(500, 260),
                 style=wx.CAPTION | wx.STAY_ON_TOP,
                 root_user='root',
                 root_pass='guess',
                 last_user='',
                 password='',
                 domains=[],
                 server='',
                 base_dn='',
                 destroy=True):
        super(LoginWindow, self).__init__(parent, title=title, size=size,
                                          style=style)
        self.panel = wx.Panel(self)
        self.root_user = root_user
        self.root_pass = root_pass
        self.last_user = last_user
        self.pwd = password
        self.current_user = None

        self.domains = domains or ['']
        self.server = server
        self.base_dn = base_dn
        self.destroy = destroy

        font = self.GetFont()
        font.SetWeight(wx.BOLD)
        font.SetPointSize(13)
        self.panel.SetFont(font)
        self.init_ui()
        self.panel.Layout()
        self.Bind(wx.EVT_BUTTON, self.on_login, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.on_quit, id=wx.ID_CANCEL)
        self.CenterOnScreen()
        self.Refresh()
        self.ShowModal()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        label_width = 150

        label_style = wx.BORDER_DOUBLE | wx.ALIGN_CENTER
        # Name field
        label = utils.add_label_field(self.panel, label='NT Name',
                                      width=label_width, style=label_style)
        label.SetForegroundColour("blue")
        self.name_tc = utils.add_text_field(self.panel, value=self.last_user)
        self.name_tc.Bind(wx.EVT_TEXT, self.on_enter_name)
        utils.add_quick_sizer(sizer, wgts=[(label, 0), (self.name_tc, 1)])

        # Password field
        label = utils.add_label_field(self.panel, label='Password',
                                      width=label_width, style=label_style)
        label.SetForegroundColour("blue")

        self.pwd_tc = utils.add_text_field(self.panel, value=self.pwd,
                                           style=wx.TE_PASSWORD)

        utils.add_quick_sizer(sizer, wgts=[(label, 0), (self.pwd_tc, 1)])

        combo_style = wx.CB_DROPDOWN | wx.CB_SORT
        if self.domains[0]:
            combo_style = combo_style | wx.CB_READONLY

        # Domain field
        label = utils.add_label_field(self.panel, label='Domain',
                                      width=label_width, style=label_style)
        label.SetForegroundColour("blue")
        self.domain_cb = wx.ComboBox(self.panel, -1,
                                     self.domains[0],
                                     choices=self.domains,
                                     style=combo_style,
                                     )
        utils.add_quick_sizer(sizer, wgts=[(label, 0), (self.domain_cb, 1)])

        line = wx.StaticLine(self.panel, -1, style=wx.LI_HORIZONTAL)
        style = wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP
        sizer.Add(line, 0, style, 5)
        btnsizer = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self.panel, wx.ID_OK, size=(100, -1))
        ok_btn.SetDefault()
        ok_btn.SetLabel('&Login')
        btnsizer.AddButton(ok_btn)

        cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, size=(100, -1))
        cancel_btn.SetLabel('&Cancel')
        btnsizer.AddButton(cancel_btn)
        btnsizer.Realize()

        style = wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL
        sizer.Add(btnsizer, 1, style, 5)

        self.panel.SetSizer(sizer)
        if self.last_user:
            if self.pwd:
                ok_btn.SetFocus()
            else:
                self.pwd_tc.SetFocus()

    def on_enter_name(self, evt=None):
        self.domain_cb.Enable('\\' not in self.name_tc.GetValue())
        evt.Skip()

    def high_light(self, wgt, focus=True):
        wgt.Clear()
        wgt.BackgroundColour = HIGHLIGHT_RED
        if focus:
            wgt.SetFocus()

    def get_field_values(self):
        self.login_name = self.name_tc.GetValue().strip().lower()
        self.password = self.pwd_tc.GetValue()
        self.domain = self.domain_cb.GetValue().strip().upper()

    def on_login(self, event):
        self.get_field_values()
        if not self.login_name:
            self.high_light(self.name_tc)
            self.Refresh()
            return

        self.name_tc.BackgroundColour = wx.WHITE
        if not self.password:
            self.name_tc.ClearBackground()
            self.high_light(self.pwd_tc)
            self.Refresh()
            return

        if self.login_name == self.root_user:
            if self.password == self.root_pass:
                self.after_login()
                return

            self.high_light(self.pwd_tc)
            self.Refresh()
            return

        if '\\' in self.login_name:
            self.domain, self.login_name = self.login_name.split('\\', 1)

        ec, msg = ldap_login(self.server, self.base_dn,
                             '{}\\{}'.format(self.domain, self.login_name),
                             self.password)
        if ec in (100, 300):
            utils.popup_msgbox(self, caption='Connection Error', msg=msg,
                               icon='warn',
                               )
            return
        elif ec == 200:
            utils.popup_msgbox(self, caption='Authentication Error',
                               msg='Username/password not match',
                               icon='error')
            self.high_light(self.pwd_tc)
            self.Refresh()
            return

        self.after_login()

    def after_login(self):
        self.current_user = self.login_name
        self.on_quit()

    def on_quit(self, event=None):
        if self.destroy:
            self.Destroy()
        else:
            self.Hide()


def test_run():
    app = wx.App()
    LoginWindow(domains=['jabil'], last_user='test', password='password')
    app.MainLoop()

if __name__ == '__main__':
    test_run()
