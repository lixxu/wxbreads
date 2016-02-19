#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import wx
from pyldaplite import ldap, PyLDAPLite
import windbreads.utils as wdutils
import widgets

HIGHLIGHT_RED = '#F75D59'


def ldap_login(server, base_dn, login_name, password, close=True):
    p = PyLDAPLite(server=server, base_dn=base_dn)
    try:
        p.connect(login_name, password)
    except ldap.SERVER_DOWN as e:
        return 100, e
    except ldap.INVALID_CREDENTIALS:
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
                 size=(500, 260),
                 style=wx.CAPTION | wx.STAY_ON_TOP,
                 root_user='root',
                 root_pass='guess',
                 last_user='',
                 password='',
                 domains=[],
                 server='',
                 base_dn='',
                 destroy=True, **kwargs):
        self.t = kwargs.get('t')
        super(LoginWindow, self).__init__(parent,
                                          title=wdutils.tr_text(title, self.t),
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
        _, self.name_tc = widgets.add_text_row(self.panel, sizer,
                                               label='NT Name', fg='blue',
                                               value=self.last_user,
                                               **kwargs)
        self.name_tc.Bind(wx.EVT_TEXT, self.on_enter_name)

        # Password
        _, self.pwd_tc = widgets.add_text_row(self.panel, sizer,
                                              label='Password', fg='blue',
                                              value=self.pwd,
                                              sstyle=wx.TE_PASSWORD,
                                              **kwargs)

        _, wgt = widgets.add_combobox(self.panel, sizer, label='Domain',
                                      fg='blue',
                                      readonly=self.domains[0],
                                      value=self.domains[0],
                                      choices=self.domains,
                                      **kwargs)
        self.domain_cb = wgt

        ok_btn, cancel_btn = widgets.add_ok_buttons(self.panel, sizer,
                                                    size=(100, -1),
                                                    ok_text='&Login', t=self.t)

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
            widgets.popup(self, caption='Connection Error', msg=msg,
                          icon='warn', t=self.t)
            return
        elif ec == 200:
            widgets.popup(self, caption='Authentication Error',
                          msg='Username/password not match',
                          icon='error', t=self.t)
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
    LoginWindow(domains=['domain'], last_user='test', password='password')
    app.MainLoop()


def test_i18n_run():
    from functools import partial
    mo = {'User Login': '用户登录', 'NT Name': '域用户名', 'Password': '密码',
          'Domain': '域', '&Login': '登录 (&L)', '&Cancel': '取消 (&C)'}
    t = partial(wdutils.tt, lang='zh', po=dict(zh=mo))
    app = wx.App()
    LoginWindow(domains=['domain'], last_user='test', password='password', t=t)
    app.MainLoop()

if __name__ == '__main__':
    test_run()
    test_i18n_run()
