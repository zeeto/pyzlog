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
