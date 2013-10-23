# -*- coding: utf8 -*-
# This file is part of PyBossa-links.
#
# Copyright (C) 2013 Daniel Lombraña González
#
# PyBossa-links is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa-links is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa-links. If not, see <http://www.gnu.org/licenses/>.
import random
from collections import namedtuple
from mnemosyne.core import create_app
from mnemosyne.model import db
from mnemosyne.model.link import Link
from mnemosyne.model.project import Project
from mnemosyne.model.throttle import Throttle
import tempfile
import os

PseudoRequest = namedtuple('PseudoRequest', ['text', 'status_code', 'headers'])


class Test(object):
    ERR_MSG_200_STATUS_CODE = 'Status code should be 200'
    ERR_MSG_404_STATUS_CODE = 'Status code should be 404'

    def setUp(self):
        self.db_fd, self.db_name = tempfile.mkstemp()

        self.app = create_app(db_name="sqlite:///" + self.db_name,
                              testing=True)

        self.db = db
        print "Using DB %s" % self.app.config['SQLALCHEMY_DATABASE_URI']
        self.app.config['TESTING'] = True
        self.tc = self.app.test_client()
        with self.app.app_context():
            self.db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_name)

    def project_fixtures(self):
        # Create projects
        with self.app.app_context():
            for i in range(0, random.randint(5, 10)):
                name = 'name_%s' % i
                slug = 'slug_%s' % i
                pb_app_short_name = name + "_" + slug
                keywords = '%s, %s, %s' % (name, slug, pb_app_short_name)
                self.db.session.add(Project(name, slug, pb_app_short_name, keywords))
            self.db.session.commit()

    def links_fixtures(self):
        # Create links
        projects = Project.query.all()
        for p in projects:
            for i in range(0, random.randint(1, 10)):
                url = 'http://%s.com/%s.jpg' % (p.slug, i)
                self.db.session.add(Link(url, p.id))
        self.db.session.commit()

    def fixtures(self):
        self.project_fixtures()
        self.links_fixtures()

    def throttle_fixtures(self):
        db.session.add(Throttle(ip="127.0.0.1", hits="1"))
        db.session.commit()
