# This file is part of the TREZOR project.
#
# Copyright (C) 2012-2016 Marek Palatinus <slush@satoshilabs.com>
# Copyright (C) 2012-2016 Pavol Rusnak <stick@satoshilabs.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
#
# The script has been modified for KeepKey device.

import unittest
import common
import binascii

import keepkeylib.messages_pb2 as proto
import keepkeylib.types_pb2 as proto_types
from keepkeylib.client import CallException
from keepkeylib.tools import int_to_big_endian

class TestMsgEthereumSigntx(common.KeepKeyTest):

    def test_ethereum_signtx_nodata(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.client.apply_policy('AdvancedMode', 0)

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0, 0],
            nonce=0,
            gas_price=20,
            gas_limit=20,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=10)
        self.assertEqual(sig_v, 27)
        self.assertEqual(binascii.hexlify(sig_r), '9b61192a161d056c66cfbbd331edb2d783a0193bd4f65f49ee965f791d898f72')
        self.assertEqual(binascii.hexlify(sig_s), '49c0bbe35131592c6ed5c871ac457feeb16a1493f64237387fab9b83c1a202f7')

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0, 0],
            nonce=123456,
            gas_price=20000,
            gas_limit=20000,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=12345678901234567890)
        self.assertEqual(sig_v, 28)
        self.assertEqual(binascii.hexlify(sig_r), '6de597b8ec1b46501e5b159676e132c1aa78a95bd5892ef23560a9867528975a')
        self.assertEqual(binascii.hexlify(sig_s), '6e33c4230b1ecf96a8dbb514b4aec0a6d6ba53f8991c8143f77812aa6daa993f')

    def test_ethereum_signtx_data(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.client.apply_policy('AdvancedMode', 0)

        with self.client:
            ret = self.client.call_raw(proto.EthereumSignTx(
                address_n=[0, 0],
                nonce=int_to_big_endian(0),
                gas_price=int_to_big_endian(20),
                gas_limit=int_to_big_endian(20),
                value=int_to_big_endian(10),
                to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
                data_initial_chunk='abcdefghijklmnop' * 64,
                data_length=1024))

            # Confirm the Output
            self.assertEqual(ret, proto.ButtonRequest(code=proto_types.ButtonRequest_ConfirmOutput))
            self.client.debug.press_yes()
            ret = self.client.call_raw(proto.ButtonAck())

            # Confirm Warning about AdvancedMode being turned off
            self.assertEqual(ret, proto.ButtonRequest(code=proto_types.ButtonRequest_Other))
            self.client.debug.press_yes()
            ret = self.client.call_raw(proto.ButtonAck())

            self.assertEqual(ret.code, proto_types.Failure_ActionCancelled)

        self.client.apply_policy('AdvancedMode', 1)

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0, 0],
            nonce=0,
            gas_price=20,
            gas_limit=20,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=10,
            data='abcdefghijklmnop' * 16)
        self.assertEqual(sig_v, 28)
        self.assertEqual(binascii.hexlify(sig_r), '6da89ed8627a491bedc9e0382f37707ac4e5102e25e7a1234cb697cedb7cd2c0')
        self.assertEqual(binascii.hexlify(sig_s), '691f73b145647623e2d115b208a7c3455a6a8a83e3b4db5b9c6d9bc75825038a')

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0, 0],
            nonce=123456,
            gas_price=20000,
            gas_limit=20000,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=12345678901234567890,
            data='ABCDEFGHIJKLMNOP' * 256 + '!!!')
        self.assertEqual(sig_v, 28)
        self.assertEqual(binascii.hexlify(sig_r), '4e90b13c45c6a9bf4aaad0e5427c3e62d76692b36eb727c78d332441b7400404')
        self.assertEqual(binascii.hexlify(sig_s), '3ff236e7d05f0f9b1ee3d70599bb4200638f28388a8faf6bb36db9e04dc544be')

        self.client.apply_policy('AdvancedMode', 0)


    def test_ethereum_signtx_message(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.client.apply_policy('AdvancedMode', 1)

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0, 0],
            nonce=0,
            gas_price=20000,
            gas_limit=20000,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=0,
            data='ABCDEFGHIJKLMNOP' * 256 + '!!!')
        self.assertEqual(sig_v, 28)
        self.assertEqual(binascii.hexlify(sig_r), '070e9dafda4d9e733fa7b6747a75f8a4916459560efb85e3e73cd39f31aa160d')
        self.assertEqual(binascii.hexlify(sig_s), '7842db33ef15c27049ed52741db41fe3238a6fa3a6a0888fcfb74d6917600e41')

    def test_ethereum_signtx_newcontract(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.client.apply_policy('AdvancedMode', 1)

        # contract creation without data should fail.
        self.assertRaises(Exception, self.client.ethereum_sign_tx,
            n=[0, 0],
            nonce=123456,
            gas_price=20000,
            gas_limit=20000,
            to='',
            value=12345678901234567890)

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0, 0],
            nonce=0,
            gas_price=20000,
            gas_limit=20000,
            to='',
            value=12345678901234567890,
            data='ABCDEFGHIJKLMNOP' * 256 + '!!!')
        self.assertEqual(sig_v, 28)
        self.assertEqual(binascii.hexlify(sig_r), 'b401884c10ae435a2e792303b5fc257a09f94403b2883ad8c0ac7a7282f5f1f9')
        self.assertEqual(binascii.hexlify(sig_s), '4742fc9e6a5fa8db3db15c2d856914a7f3daab21603a6c1ce9e9927482f8352e')

    def test_ethereum_sanity_checks(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.client.apply_policy('AdvancedMode', 1)

        # gas overflow
        self.assertRaises(Exception, self.client.ethereum_sign_tx,
            n=[0, 0],
            nonce=123456,
            gas_price=0xffffffffffffffffffffffffffffffff,
            gas_limit=0xffffffffffffffffffffffffffffff,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=12345678901234567890)

        # no gas price
        self.assertRaises(Exception, self.client.ethereum_sign_tx,
            n=[0, 0],
            nonce=123456,
            gas_limit=10000,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=12345678901234567890)

        # no gas limit
        self.assertRaises(Exception, self.client.ethereum_sign_tx,
            n=[0, 0],
            nonce=123456,
            gas_price=10000,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=12345678901234567890)

        # no nonce
        self.assertRaises(Exception, self.client.ethereum_sign_tx,
            n=[0, 0],
            gas_price=10000,
            gas_limit=123456,
            to=binascii.unhexlify('1d1c328764a41bda0492b66baa30c4a339ff85ef'),
            value=12345678901234567890)

    def test_ethereum_signtx_nodata_eip155(self):
        self.setup_mnemonic_allallall()
        self.client.apply_policy('AdvancedMode', 0)

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0x80000000 | 44, 0x80000000 | 1, 0x80000000, 0, 0],
            nonce=0,
            gas_price=20000000000,
            gas_limit=21000,
            to=binascii.unhexlify('8ea7a3fccc211ed48b763b4164884ddbcf3b0a98'),
            value=100000000000000000,
            chain_id=3)
        self.assertEqual(sig_v, 41)
        self.assertEqual(binascii.hexlify(sig_r), 'a90d0bc4f8d63be69453dd62f2bb5fff53c610000abf956672564d8a654d401a')
        self.assertEqual(binascii.hexlify(sig_s), '544a2e57bc8b4da18660a1e6036967ea581cc635f5137e3ba97a750867c27cf2')

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0x80000000 | 44, 0x80000000 | 1, 0x80000000, 0, 0],
            nonce=1,
            gas_price=20000000000,
            gas_limit=21000,
            to=binascii.unhexlify('8ea7a3fccc211ed48b763b4164884ddbcf3b0a98'),
            value=100000000000000000,
            chain_id=3)
        self.assertEqual(sig_v, 42)
        self.assertEqual(binascii.hexlify(sig_r), '699428a6950e23c6843f1bf3754f847e64e047e829978df80d55187d19a401ce')
        self.assertEqual(binascii.hexlify(sig_s), '087343d0a3a2f10842218ffccb146b59a8431b6245ab389fde22dc833f171e6e')

    def test_ethereum_signtx_data_eip155(self):
        self.setup_mnemonic_allallall()
        self.client.apply_policy('AdvancedMode', 1)

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0x80000000 | 44, 0x80000000 | 1, 0x80000000, 0, 0],
            nonce=2,
            gas_price=20000000000,
            gas_limit=21004,
            to=binascii.unhexlify('8ea7a3fccc211ed48b763b4164884ddbcf3b0a98'),
            value=100000000000000000,
            data='\0',
            chain_id=3)
        self.assertEqual(sig_v, 42)
        self.assertEqual(binascii.hexlify(sig_r), 'ba85b622a8bb82606ba96c132e81fa8058172192d15bc41d7e57c031bca17df4')
        self.assertEqual(binascii.hexlify(sig_s), '6473b75997634b6f692f8d672193591d299d5bf1c2d6e51f1a14ed0530b91c7d')

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0x80000000 | 44, 0x80000000 | 1, 0x80000000, 0, 0],
            nonce=3,
            gas_price=20000000000,
            gas_limit=299732,
            to=binascii.unhexlify('8ea7a3fccc211ed48b763b4164884ddbcf3b0a98'),
            value=100000000000000000,
            data='ABCDEFGHIJKLMNOP' * 256 + '!!!',
            chain_id=3)
        self.assertEqual(sig_v, 42)
        self.assertEqual(binascii.hexlify(sig_r), 'd021c98f92859c8db5e4de2f0e410a8deb0c977eb1a631e323ebf7484bd0d79a')
        self.assertEqual(binascii.hexlify(sig_s), '2c0e9defc9b1e895dc9520ff25ba3c635b14ad70aa86a5ad6c0a3acb82b569b6')

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0x80000000 | 44, 0x80000000 | 1, 0x80000000, 0, 0],
            nonce=4,
            gas_price=20000000000,
            gas_limit=21004,
            to=binascii.unhexlify('8ea7a3fccc211ed48b763b4164884ddbcf3b0a98'),
            value=0,
            data='\0',
            chain_id=3)
        self.assertEqual(sig_v, 42)
        self.assertEqual(binascii.hexlify(sig_r), 'dd52f026972a83c56b7dea356836fcfc70a68e3b879cdc8ef2bb5fea23e0a7aa')
        self.assertEqual(binascii.hexlify(sig_s), '079285fe579c9a2da25c811b1c5c0a74cd19b6301ee42cf20ef7b3b1353f7242')

        sig_v, sig_r, sig_s = self.client.ethereum_sign_tx(
            n=[0x80000000 | 44, 0x80000000 | 1, 0x80000000, 0, 0],
            nonce=5,
            gas_price=0,
            gas_limit=21004,
            to=binascii.unhexlify('8ea7a3fccc211ed48b763b4164884ddbcf3b0a98'),
            value=0,
            data='\0',
            chain_id=3)
        self.assertEqual(sig_v, 42)
        self.assertEqual(binascii.hexlify(sig_r), 'f7505f709d5999343aea3c384034c62d0514336ff6c6af65582006f708f81503')
        self.assertEqual(binascii.hexlify(sig_s), '44e09e29a4b6247000b46ddc94fe391e94deb2b39ad6ac6398e6db5bec095ba9')

if __name__ == '__main__':
    unittest.main()
