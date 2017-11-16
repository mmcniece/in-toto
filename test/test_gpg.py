#!/usr/bin/env python

"""
<Program Name>
  test_gpg.py

<Author>
  Santiago Torres-Arias <santiago@nyu.edu>
  Lukas Puehringer <lukas.puehringer@nyu.edu>

<Started>
  Nov 15, 2017

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Test gpg/pgp-related functions.

"""

import os
import shutil
import tempfile
import unittest

import cryptography.hazmat.primitives.serialization as serialization
import cryptography.hazmat.backends as backends

from in_toto.gpg.functions import (gpg_sign_object, gpg_export_pubkey,
    gpg_verify_signature)
from in_toto.gpg.rsa import create_key as rsa_create_key
from in_toto.gpg.dsa import create_key as dsa_create_key

import securesystemslib.formats
import securesystemslib.exceptions

class TestGPGRSA(unittest.TestCase):
  """Test signature creation, verification and key export from the gpg
  module"""

  default_keyid = "5C318D0AE3F859837526898A38343D0CB98A0422"

  @classmethod
  def setUpClass(self):
    # Create directory to run the tests without having everything blow up
    self.working_dir = os.getcwd()

    # Find demo files
    gpg_keyring_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "gpg_keyrings", "rsa")

    self.test_dir = os.path.realpath(tempfile.mkdtemp())
    self.gnupg_home = os.path.join(self.test_dir, "rsa")
    shutil.copytree(gpg_keyring_path, self.gnupg_home)
    os.chdir(self.test_dir)

  @classmethod
  def tearDownClass(self):
    """Change back to initial working dir and remove temp test directory. """
    os.chdir(self.working_dir)
    shutil.rmtree(self.test_dir)

  def test_gpg_export_pubkey(self):
    """ export a public key and make sure the parameters are the right ones:
      
      since there's very little we can do to check rsa key parameters are right
      we pre-exported the public key to an ssh key, which we can load with 
      cryptography for the sake of comparison """

    # export our gpg key, using our functions
    key_data = gpg_export_pubkey(self.default_keyid, homedir=self.gnupg_home)
    our_exported_key = rsa_create_key(key_data)

    # load the equivalent ssh key, and make sure that we get the same RSA key
    # parameters
    ssh_key_basename = "{}.ssh".format(self.default_keyid)
    ssh_key_path = os.path.join(self.gnupg_home, ssh_key_basename)
    with open(ssh_key_path, "rb") as fp:
      keydata = fp.read()

    ssh_key = serialization.load_ssh_public_key(keydata, 
        backends.default_backend()) 

    self.assertEquals(ssh_key.public_numbers().n,
        our_exported_key.public_numbers().n)
    self.assertEquals(ssh_key.public_numbers().e,
        our_exported_key.public_numbers().e)

  def test_gpg_sign_and_verify_object(self):
    """Create a signature using the deafult key on the keyring """

    test_data = b'test_data'
    wrong_data = b'something malicious'

    signature = gpg_sign_object(test_data, homedir=self.gnupg_home)
    key_data = gpg_export_pubkey(self.default_keyid, homedir=self.gnupg_home)

    self.assertTrue(gpg_verify_signature(signature, key_data, test_data))
    self.assertFalse(gpg_verify_signature(signature, key_data, wrong_data))

class TestGPGDSA(unittest.TestCase):
  """ Test signature creation, verification and key export from the gpg
  module """

  default_keyid = "3D80E7F45377F9203BDA3B4B1629F9F0883466FA"

  @classmethod
  def setUpClass(self):
    # Create directory to run the tests without having everything blow up
    self.working_dir = os.getcwd()
    self.test_dir = os.path.realpath(tempfile.mkdtemp())
    self.gnupg_home = os.path.join(self.test_dir, "dsa")

    # Find keyrings
    keyrings = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "gpg_keyrings", "dsa")

    shutil.copytree(keyrings, self.gnupg_home)
    os.chdir(self.test_dir)

  @classmethod
  def tearDownClass(self):
    """Change back to initial working dir and remove temp test directory. """
    os.chdir(self.working_dir)
    shutil.rmtree(self.test_dir)

  def test_gpg_export_pubkey(self):
    """ export a public key and make sure the parameters are the right ones:
      
      since there's very little we can do to check rsa key parameters are right
      we pre-exported the public key to an ssh key, which we can load with 
      cryptography for the sake of comparison """

    # export our gpg key, using our functions
    key_data = gpg_export_pubkey(self.default_keyid, homedir=self.gnupg_home)
    our_exported_key = dsa_create_key(key_data)

    # load the equivalent ssh key, and make sure that we get the same RSA key
    # parameters
    ssh_key_basename = "{}.ssh".format(self.default_keyid)
    ssh_key_path = os.path.join(self.gnupg_home, ssh_key_basename)
    with open(ssh_key_path, "rb") as fp:
      keydata = fp.read()

    ssh_key = serialization.load_ssh_public_key(keydata, 
        backends.default_backend()) 

    self.assertEquals(ssh_key.public_numbers().y,
        our_exported_key.public_numbers().y)
    self.assertEquals(ssh_key.public_numbers().parameter_numbers.g,
        our_exported_key.public_numbers().parameter_numbers.g)
    self.assertEquals(ssh_key.public_numbers().parameter_numbers.q,
        our_exported_key.public_numbers().parameter_numbers.q)
    self.assertEquals(ssh_key.public_numbers().parameter_numbers.p,
        our_exported_key.public_numbers().parameter_numbers.p)

  def test_gpg_sign_and_verify_object(self):
    """Create a signature using the deafult key on the keyring """

    test_data = b'test_data'
    wrong_data = b'something malicious'

    signature = gpg_sign_object(test_data, homedir=self.gnupg_home)
    key_data = gpg_export_pubkey(self.default_keyid, homedir=self.gnupg_home)

    self.assertTrue(gpg_verify_signature(signature, key_data, test_data))
    self.assertFalse(gpg_verify_signature(signature, key_data, wrong_data))


if __name__ == "__main__":
  unittest.main()
