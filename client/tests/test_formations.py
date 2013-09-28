"""
Unit tests for the Deis CLI formations commands.

Run these tests with "python -m unittest client.tests.formations"
or with "./manage.py test client.FormationsTest".
"""

from __future__ import unicode_literals
from unittest import TestCase
from uuid import uuid4
import re

import pexpect

from .utils import DEIS
from .utils import random_repo
from .utils import setup
from .utils import teardown


class FormationsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        repo_name, repo_url = random_repo()
        cls.username, cls.password, cls.repo_dir = setup(repo_url)

    @classmethod
    def tearDownClass(cls):
        teardown(cls.username, cls.password, cls.repo_dir)

    def test_list(self):
        # list formations and get their names
        child = pexpect.spawn("{} formations".format(DEIS))
        child.expect('=== Formations')
        child.expect(pexpect.EOF)
        formations_before = re.findall(r'([-_\w]+) {\w?}', child.before)
        # create a new formation
        formation = "{}-test-formation-{}".format(self.username, uuid4().hex[:4])
        child = pexpect.spawn(
            "{} formations:create {} --flavor=ec2-us-west-2".format(DEIS, formation))
        child.expect("created {}.*to scale a basic formation".format(formation))
        child.expect(pexpect.EOF)
        # list formations and get their names
        child = pexpect.spawn("{} formations".format(DEIS))
        child.expect('=== Formations')
        child.expect(pexpect.EOF)
        formations = re.findall(r'([-_\w]+) {\w?}', child.before)
        # test that the set of names contains the previous set
        self.assertLess(set(formations_before), set(formations))
        # delete the formation
        child = pexpect.spawn("{} formations:destroy {} --confirm={}".format(
            DEIS, formation, formation))
        child.expect('done in ', timeout=5*60)
        child.expect(pexpect.EOF)
        # list formations and get their names
        child = pexpect.spawn("{} formations:list".format(DEIS))
        child.expect('=== Formations')
        child.expect(pexpect.EOF)
        formations = re.findall(r'([-_\w]+) {\w?}', child.before)
        # test that the set of names is equal to the original set
        self.assertEqual(set(formations_before), set(formations))

    def test_create(self):
        formation = "{}-test-formation-{}".format(self.username, uuid4().hex[:4])
        child = pexpect.spawn(
            "{} formations:create {} --flavor=ec2-us-west-2".format(DEIS, formation))
        child.expect("created {}.*to scale a basic formation".format(formation))
        child.expect(pexpect.EOF)
        # destroy formation the one-liner way
        child = pexpect.spawn("{} formations:destroy {} --confirm={}".format(
            DEIS, formation, formation))
        child.expect('done in ', timeout=5*60)
        child.expect(pexpect.EOF)

    def test_destroy(self):
        formation = "{}-test-formation-{}".format(self.username, uuid4().hex[:4])
        child = pexpect.spawn(
            "{} formations:create {} --flavor=ec2-us-east-1".format(DEIS, formation))
        child.expect("created {}.*to scale a basic formation".format(formation))
        child.expect(pexpect.EOF)
        # destroy formation the interactive way
        child = pexpect.spawn("{} formations:destroy {}".format(DEIS, formation))
        child.expect('> ')
        child.sendline(formation)
        child.expect('done in ', timeout=5*60)
        child.expect(pexpect.EOF)
