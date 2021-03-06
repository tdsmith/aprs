#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python APRS Module APRS-IS Bindings Tests."""

import random
import unittest
import logging
import logging.handlers

import httpretty

from .context import aprs

from . import constants

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc. and Contributors'


class APRSTest(unittest.TestCase):  # pylint: disable=R0904
    """Tests for Python APRS-IS Bindings."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(aprs.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(aprs.LOG_LEVEL)
        _console_handler.setFormatter(aprs.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    @classmethod
    def random(cls, length=8, alphabet=constants.ALPHANUM):
        """
        Generates a random string for test cases.

        :param length: Length of string to generate.
        :param alphabet: Alphabet to use to create string.
        :type length: int
        :type alphabet: str
        """
        return ''.join(random.choice(alphabet) for _ in xrange(length))

    def setUp(self):  # pylint: disable=C0103
        self.fake_server = ''.join([
            'http://localhost:',
            self.random(4, constants.POSITIVE_NUMBERS),
            '/'
        ])

        self.fake_callsign = ''.join([
            self.random(1, 'KWN'),
            self.random(1, constants.NUMBERS),
            self.random(3, constants.ALPHABET),
            '-',
            self.random(1, constants.POSITIVE_NUMBERS)
        ])

        self.real_server = 'http://localhost:14580'
        self.real_callsign = '-'.join(['W2GMD', self.random(1, '123456789')])

        self._logger.debug(
            "fake_server=%s fake_callsign=%s",
            self.fake_server,
            self.fake_callsign
        )

    @httpretty.httprettified
    def test_fake_good_auth(self):
        """
        Tests authenticating against APRS-IS using a valid call+pass.
        """
        httpretty.HTTPretty.register_uri(
            httpretty.HTTPretty.POST,
            self.fake_server,
            status=204
        )

        aprs_conn = aprs.HTTP(
            user=self.fake_callsign,
            url=self.fake_server
        )
        aprs_conn.start()

        msg = '>'.join([
            self.fake_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self._logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertTrue(result)

    @httpretty.httprettified
    def test_fake_bad_auth_http(self):
        """
        Tests authenticating against APRS-IS using an invalid call+pass.
        """
        httpretty.HTTPretty.register_uri(
            httpretty.HTTPretty.POST,
            self.fake_server,
            status=401
        )

        aprs_conn = aprs.HTTP(
            user=self.fake_callsign,
            url=self.fake_server
        )
        aprs_conn.start()

        msg = '>'.join([
            self.fake_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self._logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertFalse(result)

    @unittest.skip('Test only works with real server.')
    def test_more(self):
        """
        Tests APRS-IS binding against a real APRS-IS server.
        """
        aprs_conn = aprs.HTTP(
            user=self.real_callsign,
            url=self.real_server
        )
        aprs_conn.start()

        msg = '>'.join([
            self.real_callsign,
            'APRS,TCPIP*:=3745.00N/12227.00W-Simulated Location'
        ])
        self._logger.debug(locals())

        result = aprs_conn.send(msg)

        self.assertFalse(result)
