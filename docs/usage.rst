========
Usage
========

To use pyzlog in a project::

    import pyzlog

    # initialize the zlogger
    pyzlog.init_logs(
        path='/var/log',
        target='foo_app.log',
        level=logging.DEBUG,
        server_hostname='foo.app.io',
        fields={'custom_1': None, 'custom_2': None})

    # then, log something
    pyzlog.info(extra={'custom_1': 42, 'custom_2': 'foo'})

    # log an error
    try:
        raise_value_error()
    except ValueError:
        pyzlog.error(extra={'custom_1': 'oh noes'})


To write tests for an application using pyzlog::

    import os
    import json
    import app
    import pyzlog
    import unittest2


    class TestApp(unittest2.TestCase, pyzlog.LogTest):

        def setUp(self):
            self.path = os.path.abspath('.')
            self.target = 'foo.log'
            self.remove_log()
            self.init_logs()

        def tearDown(self):
            self.remove_log()

        def test_log(self):
            app.something_that_logs()
            events = self.get_log_messages()
            self.assertEqual(1, len(events))
            expected_event = {
                'event_name': 'foo.event',
                # ...
            }
            self.assertEqual(expected_event, json.loads(events[0]))
