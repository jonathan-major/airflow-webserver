from __future__ import print_function

from nose.tools import eq_, ok_, raises
import unittest
import os
import datetime
import random
import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA, Model, has_access, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.views import ModelView, BaseView

from sqlalchemy import Column, Integer, String, Date, Float

from airflow_webserver.security import init_role

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


class SomeModel(Model):
    id = Column(Integer, primary_key=True)
    field_string = Column(String(50), unique=True, nullable=False)
    field_integer = Column(Integer())
    field_float = Column(Float())
    field_date = Column(Date())

    def __repr__(self):
        return str(self.field_string)


class SomeModelView(ModelView):
    datamodel = SQLAInterface(SomeModel)
    base_permissions = ['can_list', 'can_show', 'can_add', 'can_edit', 'can_delete']
    list_columns = ['field_string', 'field_integer', 'field_float', 'field_date']


class SomeBaseView(BaseView):
    route_base = ''

    @expose('/some_action')
    @has_access
    def some_action(self):
        return "action!"


class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        self.app.config['SECRET_KEY'] = 'secret_key'
        self.app.config['CSRF_ENABLED'] = False
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.appbuilder.add_view(SomeBaseView, "SomeBaseView", category="BaseViews")
        self.appbuilder.add_view(SomeModelView, "SomeModelView", category="ModelViews")

        role_admin = self.appbuilder.sm.find_role('Admin')
        self.user = self.appbuilder.sm.add_user('admin', 'admin', 'user', 'admin@fab.org', role_admin, 'general')
        log.debug("Complete setup!")

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None
        log.debug("Complete teardown!")

    def test_init_role_baseview(self):
        role_name = 'MyRole1'
        role_perms = ['can_some_action']
        role_vms = ['SomeBaseView']
        init_role(self.appbuilder.sm, role_name, role_vms, role_perms)
        role = self.appbuilder.sm.find_role(role_name)
        self.assertIsNotNone(role)
        self.assertEqual(len(role_perms), len(role.permissions))

    def test_init_role_modelview(self):
        role_name = 'MyRole2'
        role_perms = ['can_list', 'can_show', 'can_add', 'can_edit', 'can_delete']
        role_vms = ['SomeModelView']
        init_role(self.appbuilder.sm, role_name, role_vms, role_perms)
        role = self.appbuilder.sm.find_role(role_name)
        self.assertIsNotNone(role)
        self.assertEqual(len(role_perms), len(role.permissions))

    def test_invalid_perms(self):
        role_name = 'MyRole3'
        role_perms = ['can_foo']
        role_vms = ['SomeBaseView']
        with self.assertRaises(Exception) as context:
            init_role(self.appbuilder.sm, role_name, role_vms, role_perms)
        self.assertEqual("The following permissions are not valid: ['can_foo']", str(context.exception))

    def test_invalid_vms(self):
        role_name = 'MyRole4'
        role_perms = ['can_some_action']
        role_vms = ['NonExistentBaseView']
        with self.assertRaises(Exception) as context:
            init_role(self.appbuilder.sm, role_name, role_vms, role_perms)
        self.assertEqual("The following view menus are not valid: ['NonExistentBaseView']", str(context.exception))
