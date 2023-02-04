# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <lightapt.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

import os
import tornado.web

class BaseLoginHandler(tornado.web.RequestHandler):
    """
        Basic login handler for login module
    """
    def get_current_user(self):
        return self.get_secure_cookie("user")

class IndexHtml(BaseLoginHandler):
    """
        Render the index.html file
    """
    def get(self):
        self.render("index.html")

class ClientHtml(BaseLoginHandler):
    """
        Render the client.html file
    """
    @tornado.web.authenticated
    def get(self):
        self.render("client.html")

class DesktopHtml(BaseLoginHandler):
    """
        Render the desktop.html file
    """
    @tornado.web.authenticated
    def get(self):
        with open(os.path.join(os.getcwd(),"client","templates","ndesktop.html"), 'rb') as f:
            self.write(f.read())
            self.finish()

class DesktopSystemHtml(BaseLoginHandler):
    """
        Render the ndesktop-system.html file
    """
    @tornado.web.authenticated
    def get(self):
        with open(os.path.join(os.getcwd(),"client","templates","ndesktop-system.html"), 'rb') as f:
            self.write(f.read())
            self.finish()

class DesktopBrowserHtml(BaseLoginHandler):
    """
        Render the ndesktop-browser.html file
    """
    @tornado.web.authenticated
    def get(self):
        with open(os.path.join(os.getcwd(),"client","templates","ndesktop-browser.html"), 'rb') as f:
            self.write(f.read())
            self.finish()

class DesktopStoreHtml(BaseLoginHandler):
    """
        Render the ndesktop-store.html file
    """
    @tornado.web.authenticated
    def get(self):
        with open(os.path.join(os.getcwd(),"client","templates","ndesktop-store.html"), 'rb') as f:
            self.write(f.read())
            self.finish()

class DebugHtml(BaseLoginHandler):
    """
        Render debug.html file
    """
    @tornado.web.authenticated
    def get(self):
        with open(os.path.join(os.getcwd(),"client","templates","debug.html"), 'rb') as f:
            self.write(f.read())
            self.finish()

class BugReportHtml(BaseLoginHandler):
    """
        Render a bug report html file
    """
    @tornado.web.authenticated
    def get(self):
        self.render("bugreport.html")

class WebSSHHtml(BaseLoginHandler):
    """
        Redirects to webssh server
    """
    @tornado.web.authenticated
    def get(self):
        self.redirect("http://127.0.0.1:8888/",status=301)

class NoVNCHtml(BaseLoginHandler):
    """
        NoVNC html file container
    """
    @tornado.web.authenticated
    def get(self):
        self.render("novnc.html")

class SkymapHtml(BaseLoginHandler):
    """
        Render a skymap html file
    """
    @tornado.web.authenticated
    def get(self):
        self.render("skymap.html")

class TestHtml(tornado.web.RequestHandler):
    def get(self):
        self.render("test.html")

class DeviceHtml(tornado.web.RequestHandler):
    def get(self):
        self.render("device.html")