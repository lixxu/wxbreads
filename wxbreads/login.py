#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx
try:
    from pyldaplite import ldap, PyLDAPLite as LDAP

    SERVER_DOWN_ERROR = ldap.SERVER_DOWN
    INVALID_CREDENTIALS_ERROR = ldap.INVALID_CREDENTIALS
except ImportError:
    from ldap3tool import ldap3, LDAPTool as LDAP

    SERVER_DOWN_ERROR = ldap3.core.exceptions.LDAPSocketOpenError
    INVALID_CREDENTIALS_ERROR = ldap3.core.exceptions.LDAPBindError

import windbreads.utils as wdu
import wxbreads.widgets as wxw

HIGHLIGHT_RED = '#F75D59'


def ldap_login(server, base_dn, login_name, password, close=True):
    p = LDAP(server=server, base_dn=base_dn)
    try:
        p.connect(login_name, password)
    except SERVER_DOWN_ERROR as e:
        return 100, e
    except INVALID_CREDENTIALS_ERROR:
        return 200, None
    except Exception as e:
        return 300, e
    else:
        if close:
            p.close()
        else:
            return 0, p

    return 0, None


class LoginWindow(wx.Dialog):
    def __init__(self, parent=None, title='User Login',
                 size=(500, 240),
                 style=wx.CAPTION | wx.STAY_ON_TOP,
                 root_user='root',
                 root_pass='guess',
                 last_user='',
                 password='',
                 domains=[],
                 server='cnshac0dc10',
                 base_dn='dc=corp,dc=jabil,dc=org',
                 destroy=True, **kwargs):
        self.t = kwargs.get('t')
        self.enable_cancel = kwargs.get('enable_cancel', True)
        super(LoginWindow, self).__init__(parent,
                                          title=wdu.ttt(title, self.t),
                                          size=size, style=style)
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
        size = (150, 30)
        label_style = wx.BORDER_DOUBLE | wx.ALIGN_CENTER
        kwargs = dict(fsize=size, fstyle=label_style, t=self.t)

        # Name field
        _, self.name_tc = wxw.add_text_row(self.panel, sizer,
                                           label='NT Name', fg='blue',
                                           value=self.last_user,
                                           **kwargs)
        wxw.set_fg(self.name_tc, 'black')
        self.name_tc.Bind(wx.EVT_TEXT, self.on_enter_name)

        # Password
        _, self.pwd_tc = wxw.add_text_row(self.panel, sizer,
                                          label='Password', fg='blue',
                                          value=self.pwd,
                                          sstyle=wx.TE_PASSWORD,
                                          **kwargs)
        wxw.set_fg(self.pwd_tc, 'black')
        _, wgt = wxw.add_combobox(self.panel, sizer, label='Domain',
                                  fg='blue',
                                  readonly=self.domains[0],
                                  value=self.domains[0],
                                  choices=self.domains,
                                  **kwargs)
        wxw.set_fg(wgt, 'black')
        self.domain_cb = wgt

        ok_btn, cancel_btn = wxw.add_ok_buttons(self.panel, sizer,
                                                size=(100, -1),
                                                ok_text='&Login', t=self.t)

        self.ok_btn = ok_btn
        self.cancel_btn = cancel_btn
        cancel_btn.Enable(self.enable_cancel)
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
        self.domain = self.domain_cb.GetValue().strip().lower()

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
            wxw.popup(self, caption='Error', msg=msg, icon='e', t=self.t)
            return
        elif ec == 200:
            wxw.popup(self, caption='Authentication Error',
                      msg='Username/password not match', icon='e', t=self.t)
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
    LoginWindow(domains=['jabil'], last_user='xul15', password='Python$sanic')
    app.MainLoop()


def test_i18n_run():
    from functools import partial
    import windbreads.common_i18n as wdi18n
    t = partial(wdu.tt, lang='zh', po=dict(zh=wdi18n.zh))
    app = wx.App()
    LoginWindow(domains=['domain'], last_user='test', password='password', t=t)
    app.MainLoop()

if __name__ == '__main__':
    test_run()
    test_i18n_run()
