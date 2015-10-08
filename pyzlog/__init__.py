# -*- coding: utf-8 -*-

"""Provides a drop in solution for logging json messages in a standard format.
An example of what a json log entry will look like::
    {
        "server_hostname": "localhost",
        "event_timestamp": "2015-10-31T01:01:01.42Z",
        "event_name": "foo.event",
        "log_level": "INFO",
        "application_name": "fizzbuzz",
        "fields": {
            "custom-field": 42,
            "other-custom-thing": "fizzle"
        }
    }

server_hostname, event_timestamp, event_name, log_level,
application_name, and fields will be present in every log entry.

"""

import os
import json
import socket
import logging
import logging.handlers
import traceback
import datetime
import functools

__author__ = 'zeeto.io'
__version__ = '0.1.0'

default_date_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
level_map = {
    'emergency': ('critical', 'EMERGENCY'),
    'alert': ('info', 'ALERT'),
    'notice': ('info', 'NOTICE'),
    'info': ('info', 'INFO'),
    'warning': ('warning', 'WARNING'),
    'error': ('error', 'ERROR'),
    'critical': ('critical', 'CRITICAL'),
    'debug': ('debug', 'DEBUG')
}
"""check out the level_map"""


def _default_json_default(obj):
    """ Coerce everything to strings.
    All objects representing time get output according to default_date_fmt.
    """
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.strftime(default_date_fmt)
    else:
        return str(obj)


class JsonFormatter(logging.Formatter):
    """ JsonFormatter is used internally by the pyzlog package; you
    should never have to instantiate this yourself. Takes a
    logging.LogRecord and formats it into a standardized json
    format.

    :param fmt: passed to logging.Formatter
    :param datefmt: format for timestamp field. passed to logging.Formatter
    :param application_name: app name to add to each log entry
    :param server_hostname: hostname to add to each log entry
    :param fields: whitelist of allowed fields for each log entry
    :type fmt: string
    :type datefmt: string
    :type application_name: string
    :type server_hostname: string
    :type fields: dict

    """

    def __init__(self,
                 fmt=None,
                 json_default=_default_json_default,
                 application_name='default',
                 server_hostname=None,
                 fields=None):
        self.json_default = json_default
        if server_hostname is None:
            server_hostname = os.getenv('HOSTNAME')
            if server_hostname is None:
                server_hostname = socket.gethostname()
            else:
                server_hostname = 'localhost'
        self.fields = fields.copy() if fields else {}
        self.fields.update(exception=None)
        self.defaults = {'application_name': application_name,
                         'server_hostname': server_hostname}

    def format(self, record):
        """formats a logging.Record into a standard json log entry

        :param record: record to be formatted
        :type record: logging.Record
        :return: the formatted json string
        :rtype: string
        """

        record_fields = record.__dict__.copy()
        self._set_exc_info(record_fields)

        event_name = 'default'
        if record_fields.get('event_name'):
            event_name = record_fields.pop('event_name')

        log_level = 'INFO'
        if record_fields.get('log_level'):
            log_level = record_fields.pop('log_level')

        [record_fields.pop(k) for k in record_fields.keys()
         if k not in self.fields]

        defaults = self.defaults.copy()
        fields = self.fields.copy()
        fields.update(record_fields)
        filtered_fields = {}
        for k, v in fields.iteritems():
            if v is not None:
                filtered_fields[k] = v

        defaults.update({
            'event_timestamp': self._get_now(),
            'event_name': event_name,
            'log_level': log_level,
            'fields': filtered_fields})

        return json.dumps(defaults, default=self.json_default)

    def _set_exc_info(self, record_fields):
        if 'exc_info' in record_fields:
            if record_fields['exc_info']:
                exc_info = traceback.format_exception(
                    *record_fields['exc_info'])
                if exc_info != ['None\n']:
                    record_fields['exception'] = exc_info
            record_fields.pop('exc_info')

    def _get_now(self):
        return datetime.datetime.utcnow().strftime(default_date_fmt)


def init_logs(path=None,
              target=None,
              logger_name='root',
              level=logging.DEBUG,
              maxBytes=1*1024*1024,
              backupCount=5,
              application_name='default',
              server_hostname='localhost',
              fields=None):
    """Initialize the zlogger.

    Sets up a rotating file handler to the specified path and file with
    the given size and backup count limits, sets the default
    application_name, server_hostname, and default/whitelist fields.

    :param path: path to write the log file
    :param target: name of the log file
    :param logger_name: name of the logger (defaults to root)
    :param level: log level for this logger (defaults to logging.DEBUG)
    :param maxBytes: size of the file before rotation (default 1MB)
    :param application_name: app name to add to each log entry
    :param server_hostname: hostname to add to each log entry
    :param fields: default/whitelist fields.
    :type path: string
    :type target: string
    :type logger_name: string
    :type level: int
    :type maxBytes: int
    :type backupCount: int
    :type application_name: string
    :type server_hostname: string
    :type fields: dict
    """
    log_file = os.path.abspath(
        os.path.join(path, target))
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=maxBytes, backupCount=backupCount)
    handler.setLevel(level)

    handler.setFormatter(
        JsonFormatter(
            application_name=application_name,
            server_hostname=server_hostname,
            fields=fields))

    logger.addHandler(handler)


def _log(logger_name='root', event_name=None,
         _type=None, exc_info=False, extra=None):
    extra = extra.copy() if extra else {}
    method, log_level = level_map.get(_type, ('info', 'INFO'))
    extra.update(event_name=event_name, log_level=log_level)
    getattr(logging.getLogger(logger_name), method)(
        '', exc_info=exc_info, extra=extra)


def _log_fn(exc_info=False):
    def wrap(logfunc):
        @functools.wraps(logfunc)
        def wrapped(*args, **kwargs):
            kwargs.update(_type=logfunc.__name__, exc_info=exc_info)
            return _log(*args, **kwargs)
        return wrapped
    return wrap


@_log_fn()
def emergency(**kwargs):
    """log with pyzlog level EMERGENCY"""
    pass


@_log_fn()
def alert(**kwargs):
    """log with pyzlog level ALERT"""
    pass


@_log_fn()
def notice(**kwargs):
    """log with pyzlog level NOTICE"""
    pass


@_log_fn()
def info(**kwargs):
    """log with pyzlog level INFO"""
    pass


@_log_fn()
def warning(**kwargs):
    """log with pyzlog level WARNING"""
    pass


@_log_fn(exc_info=True)
def error(**kwargs):
    """log with pyzlog level ERROR

    exception info is added if it exists
    """
    pass


@_log_fn()
def critical(**kwargs):
    """log with pyzlog level CRITICAL"""
    pass


@_log_fn()
def debug(**kwargs):
    """log with pyzlog level DEBUG"""
    pass
