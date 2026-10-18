import socket
import unittest
from unittest.mock import patch,MagicMock
from dart_network import endpoint

class DartNetworkTests(unittest.TestCase):
    def test_dns_failure_is_distinct(self):
        with patch('dart_network.socket.getaddrinfo',side_effect=socket.gaierror()):
            result=endpoint('opendart.fss.or.kr')
        self.assertEqual(result['stage'],'DNS')
        self.assertEqual(result['result'],'gaierror')

    def test_tcp_timeout_occurs_before_tls(self):
        addresses=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('203.0.113.1',443))]
        connection=MagicMock()
        connection.__enter__.return_value=connection
        connection.connect.side_effect=TimeoutError()
        with patch('dart_network.socket.getaddrinfo',return_value=addresses),patch('dart_network.socket.socket',return_value=connection),patch('dart_network.ssl.create_default_context') as tls:
            result=endpoint('opendart.fss.or.kr')
        self.assertEqual(result['stage'],'TCP 443')
        self.assertEqual(result['result'],'TimeoutError')
        tls.assert_not_called()

    def test_only_fixed_service_hosts(self):
        with self.assertRaises(ValueError):endpoint('127.0.0.1')

if __name__=='__main__':unittest.main()
