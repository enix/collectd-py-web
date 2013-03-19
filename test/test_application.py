#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock

from collectdweb.application import get_sign
from collectdweb.plugins import Signature


class TestSignature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.signature_patch = mock.patch( 'collectdweb.application.signature', spec=Signature)
    def setUp(self):
        self.signature = self.signature_patch.start()
        self.signature.sign.return_value = '<sign>'
    def tearDown(self):
        self.signature_patch.stop()

    def test_sign_json(self):
        with mock.patch('bottle.request', json = { 'url' : [
            '/hosts/xen-5/load/load.png',
            ]}):
            signed = get_sign()
        self.assertEqual( signed, [
            '/exports/hosts/xen-5/load/load.png?sign=<sign>',
            ])
        self.signature.sign.assert_called_once_with( '/exports/hosts/xen-5/load/load.png')

    def test_sign_post(self):
        with mock.patch('bottle.request', json = None) as request:
            request.POST.getall.return_value = [
                    '/hosts/xen-5/load/load.png'
                    ]
            signed = get_sign()
        request.POST.getall.assert_called_once_with( 'url')
        self.assertEqual( signed, [
            '/exports/hosts/xen-5/load/load.png?sign=<sign>',
            ])
        self.signature.sign.assert_called_once_with( '/exports/hosts/xen-5/load/load.png')
