#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyzlog
----------------------------------

Tests for `pyzlog` module.
"""

import os
import socket
import datetime
import unittest2
import mock
import pyzlog
import json
from genty import genty, genty_dataset, genty_dataprovider


class TestJsonFormatter(unittest2.TestCase):
    def test_init_defaults(self):
        doc = pyzlog.JsonFormatter(server_hostname='localhost')
        self.assertEqual({'exception': None}, doc.fields)
        self.assertDictEqual({'application_name': 'default',
                              'server_hostname': 'localhost'},
                             doc.defaults)

    def test_resolve_hostname_given(self):
        doc = pyzlog.JsonFormatter()
        self.assertEqual('fizzletov', doc.resolve_hostname('fizzletov'))

    def test_resolve_hostname_environ(self):
        doc = pyzlog.JsonFormatter()
        os.environ['HOSTNAME'] = 'bazinga'
        self.assertEqual(os.environ['HOSTNAME'], doc.resolve_hostname())
        os.environ.pop('HOSTNAME')

    def test_resolve_hostname_socket(self):
        doc = pyzlog.JsonFormatter()
        self.assertEqual(socket.gethostname(), doc.defaults['server_hostname'])

    def test_init(self):
        fields = {'foo': 'bar', 'baz': 'buzz'}
        application_name = 'app_name'
        server_hostname = 'abc.xyz'
        doc = pyzlog.JsonFormatter(application_name=application_name,
                                   server_hostname=server_hostname,
                                   fields=fields)
        # exception is always whitelisted
        fields.update(exception=None)
        self.assertDictEqual(fields, doc.fields)
        self.assertDictEqual({'application_name': application_name,
                              'server_hostname': server_hostname},
                             doc.defaults)


@genty
class TestPyzlog(unittest2.TestCase, pyzlog.LogTest):

    def setUp(self):
        self.path = os.path.abspath('.')
        self.target = 'foo.log'
        self.remove_log()

    def tearDown(self):
        self.remove_log()

    def get_mock_now(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        pyzlog.JsonFormatter._get_now = mock.MagicMock(return_value=now)
        return now

    @genty_dataset(
        ('info', 'INFO', 'info_event'),
        ('emergency', 'EMERGENCY', 'emergency_event'),
        ('alert', 'ALERT', 'alert_event'),
        ('notice', 'NOTICE', 'notice_event'),
        ('warning', 'WARNING', 'warning_event'),
        ('error', 'ERROR', 'error_event'),
        ('critical', 'CRITICAL', 'critical_event'),
        ('debug', 'DEBUG', 'debug_event'),
    )
    def level_provider(self, method, log_level, event_name):
        return (method, log_level, event_name)

    @genty_dataprovider(level_provider)
    def test_log(self, method, log_level, event_name):
        now = self.get_mock_now()
        self.init_logs()
        fields = {'extra': 'data ftw'}
        getattr(pyzlog, method)(event_name=event_name, extra=fields)
        expected_event = {
            'server_hostname': 'localhost',
            'event_timestamp': now,
            'event_name': event_name,
            'log_level': log_level,
            'application_name': 'default',
            'fields': fields}
        events = self.get_log_messages()
        self.assertEqual(1, len(events))
        self.assertEqual(expected_event, json.loads(events[0]))

    @genty_dataprovider(level_provider)
    def test_log_extra_honors_whitelist(self, method, log_level, event_name):
        self.init_logs()
        fields = {'ignored': 42}
        getattr(pyzlog, method)(event_name=event_name,
                                extra=fields)
        events = self.get_log_messages()
        self.assertEqual(1, len(events))
        self.assertNotIn('ignored', json.loads(events[0])['fields'])

    @genty_dataprovider(level_provider)
    def test_log_extra_filters_none_vals(self, method, log_level, event_name):
        fields = {'filtered': None}
        self.init_logs(extra=fields)
        getattr(pyzlog, method)(event_name=event_name,
                                extra=fields)
        events = self.get_log_messages()
        self.assertEqual(1, len(events))
        self.assertNotIn('filtered', json.loads(events[0])['fields'])

    @genty_dataprovider(level_provider)
    def test_log_extra_with_dates(self, method, log_level, event_name):
        fields = {'nested': [{'one': datetime.datetime.now(),
                              'two': {'three': datetime.time()}},
                             datetime.date(2010, 10, 10)]}
        self.init_logs(extra=fields)
        getattr(pyzlog, method)(event_name=event_name,
                                extra=fields)
        events = self.get_log_messages()
        self.assertEqual(1, len(events))
        event_fields = json.loads(events[0])['fields']
        self.assertIn('nested', event_fields)
        self.assertEqual(2, len(event_fields['nested']))
        self.assertEqual(['one', 'two'],
                         sorted(event_fields['nested'][0].keys()))
        self.assertIn('three', event_fields['nested'][0]['two'])

    def test_log_error(self):
        self.init_logs()
        try:
            raise ValueError('foo bar baz')
        except ValueError:
            pyzlog.error()
        events = self.get_log_messages()
        self.assertEqual(1, len(events))
        event = json.loads(events[0])
        self.assertIn('exception', event['fields'])
        self.assertIn('ValueError: foo bar baz\n',
                      event['fields']['exception'])
