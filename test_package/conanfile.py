from conans import ConanFile, CMake
import sys
import os.path
sys.path.append(os.getcwd() + '/../')
import imp
imported_class = imp.load_source('test.conafile', os.getcwd() + '/../conanfile.py')

############### CONFIGURE THESE VALUES ##################
default_user = "conan"
default_channel = "testing"
#########################################################

username = os.getenv("CONAN_USERNAME", default_user)
channel = os.getenv("CONAN_CHANNEL", default_channel)

class BryBaseTest(imported_class.FltkConan):
	def test(self):
		pass
		
	def build(self):
		pass

	def requirements(self):
		self.requires.add("%s/%s@%s/%s" % (self.name, self.version, username, channel))
