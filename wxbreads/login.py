#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import ldap3
import wx
import windbreads.utils as wdu
import wxbreads.widgets as wxw

from ldap3tool import LDAPTool
from wxbreads.base import BaseDialog


def ldap_login(server, base_dn, login_name, password, close=True, **kwargs):
    ldap = LDAPTool(server=server, base_dn=base_dn)
    try:
        use_ssl = kwargs.pop("use_ssl", False)
        kw = kwargs.copy()
        if use_ssl:
            kw.update(server=ldap.open_server(use_ssl=use_ssl))

        ldap.connect(login_name, password, **kw)
    except ldap3.core.exceptions.LDAPSocketOpenError as ex:
        return 100, ex
    except ldap3.core.exceptions.LDAPBindError:
        return 200, None
    except Exception as ex:
        return 300, ex
    else:
        if close:
            ldap.close()
        else:
            return 0, ldap

    return 0, None


class LoginWindow(BaseDialog):
    app_title = "User Login"

    def __init__(self, **kwargs):
        self.enable_cancel = kwargs.get("enable_cancel", True)
        self.ldap_kwargs = kwargs.pop("ldap_kwargs", {})
        self.need_busy = kwargs.pop("need_busy", False)

        super(LoginWindow, self).__init__(**kwargs)
        self.panel = wx.Panel(self)
        self.parent = parent = kwargs.get("parent")
        root_user = kwargs.get("root_user")
        root_pass = kwargs.get("root_pass")
        last_user = kwargs.get("last_user")
        if parent:
            if not root_user:
                root_user = getattr(parent, "root_user", "root")

            if not root_pass:
                root_pass = getattr(parent, "root_pass", "")

            if not last_user:
                last_user = getattr(parent, "login_user")

        self.root_user = root_user or "root"
        self.root_pass = root_pass or ""
        self.last_user = last_user or ""
        self.pwd = kwargs.get("password", "")
        self.current_user = None

        self.domains = kwargs.get("domains") or [""]
        self.server = kwargs.get("server", "ldap-server")
        self.base_dn = kwargs.get("base_dn", "dc=corp,dc=company,dc=org")
        self.destroy = kwargs.get("destroy", True)
        self.can_exit = kwargs.get("can_exit", True)
        self.is_login = False

        self.setup_ui()
        self.Bind(wx.EVT_BUTTON, self.on_login, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.on_quit, id=wx.ID_CANCEL)
        self.show()

    def setup_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        size = (120, -1)
        label_style = wx.ALIGN_RIGHT
        kwargs = dict(
            fsize=size, ssize=(200, -1), fstyle=label_style, t=self.t
        )

        # Name field
        _, self.name_tc = wxw.add_text_row(
            self.panel, sizer, label="NT Name", value=self.last_user, **kwargs
        )
        # wxw.set_fg(self.name_tc, 'black')
        self.name_tc.Bind(wx.EVT_TEXT, self.on_enter_name)
        wxw.focus_on(self.name_tc)

        # Password
        _, self.pwd_tc = wxw.add_text_row(
            self.panel,
            sizer,
            label="Password",
            value=self.pwd,
            sstyle=wx.TE_PASSWORD,
            **kwargs
        )
        # wxw.set_fg(self.pwd_tc, 'black')
        _, wgt = wxw.add_combobox(
            self.panel,
            sizer,
            label="Domain",
            readonly=self.domains[0],
            value=self.domains[0],
            choices=self.domains,
            **kwargs
        )
        # wxw.set_fg(wgt, 'black')
        self.domain_cb = wgt

        ok_btn, cancel_btn = wxw.add_ok_buttons(
            self.panel, sizer, size=(100, -1), ok_text="Login", t=self.t
        )

        self.ok_btn = ok_btn
        self.cancel_btn = cancel_btn
        cancel_btn.Enable(self.enable_cancel)

        self.panel.SetSizer(sizer)
        self.panel.Layout()
        sizer.Fit(self)

    def on_enter_name(self, evt=None):
        self.domain_cb.Enable("\\" not in self.name_tc.GetValue())
        evt.Skip()

    def high_light(self, wgt, focus=True):
        wgt.Clear()
        wgt.SetBackgroundColour(wxw.HIGHLIGHT_RED)
        if focus:
            wgt.SetFocus()

    def get_field_values(self):
        self.login_name = self.name_tc.GetValue().strip().lower()
        self.password = self.pwd_tc.GetValue()
        self.domain = self.domain_cb.GetValue().strip().lower()

    def on_login(self, event):
        self.ok_btn.Enable(False)
        self.cancel_btn.Enable(False)
        self.is_login = True
        self.current_user = None
        self.start_delay_work(self.after_submit, self.do_submit)

    def after_submit(self, delay_result):
        try:
            delay_result.get()
        except Exception as e:
            self.popup("Error", e, "e")

        self.ok_btn.Enable(True)
        self.cancel_btn.Enable(True)
        self.is_login = False
        if self.current_user:
            if self.parent and hasattr(self.parent, "login_user"):
                self.parent.login_user = self.current_user

            self.can_exit = True
            self.destroy = True
            self.on_quit()

    def do_submit(self):
        self.get_field_values()
        if not self.login_name:
            self.high_light(self.name_tc)
            self.Refresh()
            return

        self.name_tc.SetBackgroundColour(wx.NullColour)
        if not self.password:
            self.name_tc.ClearBackground()
            self.high_light(self.pwd_tc)
            self.Refresh()
            return

        if self.login_name == self.root_user:
            if self.password == self.root_pass:
                self.current_user = self.login_name
                return

            self.high_light(self.pwd_tc)
            self.Refresh()
            return

        if "\\" in self.login_name:
            self.domain, self.login_name = self.login_name.split("\\", 1)

        if self.need_busy:
            busy = self.show_busy("connecting to server...")

        ec, msg = ldap_login(
            self.server,
            self.base_dn,
            "{}\\{}".format(self.domain, self.login_name),
            self.password,
            **self.ldap_kwargs
        )
        if self.need_busy:
            del busy

        if ec in (100, 300):
            self.popup("Error", msg, "e")
            return
        elif ec == 200:
            self.popup(
                "Authentication Error", "Username/password not match", "e"
            )
            self.high_light(self.pwd_tc)
            self.Refresh()
            return

        self.current_user = self.login_name

    def on_quit(self, event=None):
        if not self.is_login and self.can_exit:
            if self.destroy:
                self.Destroy()
            else:
                self.Hide()


def test_run():
    app = wx.App()
    LoginWindow(domains=["domain"], last_user="username", password="password")
    app.MainLoop()


def test_i18n_run():
    from functools import partial
    import windbreads.common_i18n as wdi18n

    zh = wdi18n.zh
    zh.setdefault("User Login", "用户登录")
    t = partial(wdu.tt, lang="zh", po=dict(zh=zh))
    app = wx.App()
    LoginWindow(domains=["domain"], last_user="test", password="password", t=t)
    app.MainLoop()


if __name__ == "__main__":
    test_run()
    test_i18n_run()
