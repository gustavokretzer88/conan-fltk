from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os
import itertools
import shutil
global str

class FltkConan(ConanFile):
	name = "fltk"
	version = "1.3.4-1"
	settings = {
		"os": ["Windows", "Linux", "Macos"], 
		"arch": ["x86", "x86_64"],
		"compiler" : ["gcc", "Visual Studio", "apple-clang"],
		"build_type": ["Debug", "Release"]
	}
	build_policy = "missing"
	exports = "CMakeLists.txt"
	generators = "cmake", "txt"	
	configure_options = ""
	
	options = {
		"enable_cygwin": ["no", "yes", None],
		"enable_x11": ["no", "yes", None],
		"enable_cairoext": ["no", "yes", None],
		"enable_cairo": ["no", "yes", None],
		"enable_cp936": ["no", "yes", None],
		"enable_gl": ["no", "yes", None],
		"enable_shared": ["no", "yes", None],
		"enable_threads": ["no", "yes", None],
		"disable_largefile": [True, False],
		"enable_localjpeg": ["no", "yes", "auto"],
		"enable_localzlib": ["no", "yes", "auto"],
		"enable_localpng": ["no", "yes", "auto"],
		"enable_xinerama": ["no", "yes", None],
		"enable_xft": ["no", "yes", None],
		"enable_xdbe": ["no", "yes", None],
		"enable_xfixes": ["no", "yes", None],
		"enable_xcursor": ["no", "yes", None],
		"enable_xrender": ["no", "yes",None]
	}
	default_options = '''
enable_cygwin=no
enable_x11=no
enable_cairoext=no
enable_cairo=no
enable_cp936=no
enable_gl=no
enable_shared=no
enable_threads=yes
disable_largefile=False
enable_localjpeg=yes
enable_localzlib=yes
enable_localpng=yes
enable_xinerama=yes
enable_xft=yes
enable_xdbe=yes
enable_xfixes=yes
enable_xcursor=yes
enable_xrender=yes
'''
	def source(self):
		source_tgz = "http://fltk.org/pub/fltk/1.3.4/fltk-" + self.version + "-source.tar.gz"
		self.output.info("Downloading %s" % source_tgz)
		src_file_name = "fltk.tar.gz"
		tools.download(source_tgz, src_file_name)
		tools.check_md5(src_file_name, "ce21e095cf258c8bc62ce6bb605ef813")
		tools.unzip(src_file_name, ".")
		os.rename("fltk-" + self.version, "fltk")		
		os.remove(src_file_name)
		shutil.move("fltk/CMakeLists.txt", "fltk/CMakeListsOriginal.cmake")
		shutil.move("CMakeLists.txt", "fltk/CMakeLists.txt")

	def setConfigureOptions(self, optionName, option):
		self.configure_options += " --%s=%s" % (optionName, option.__str__()) if option.__str__() != "None" else ""

	def build_unix(self):
		env_build = AutoToolsBuildEnvironment(self)
		env_build.fpic =True
		with tools.environment_append(env_build.vars):
			change_build_dir = "cd fltk && "
			configure_cmd = "./configure"
			make_cmd = "make -j%d" % (tools.cpu_count())
			self.configure_options = ""
			self.setConfigureOptions("enable-cygwin"	, self.options.enable_cygwin)
			self.setConfigureOptions("enable-x11"		, self.options.enable_x11)
			self.setConfigureOptions("enable-cairoext"	, self.options.enable_cairoext)
			self.setConfigureOptions("enable-cairo"		, self.options.enable_cairo)
			self.setConfigureOptions("enable-gl"		, self.options.enable_gl)
			self.setConfigureOptions("enable-shared"	, self.options.enable_shared)
			self.setConfigureOptions("enable-threads"	, self.options.enable_threads)
			self.setConfigureOptions("enable-localjpeg"	, self.options.enable_localjpeg)
			self.setConfigureOptions("enable-localzlib"	, self.options.enable_localzlib)
			self.setConfigureOptions("enable-localpng"	, self.options.enable_localpng)
			self.setConfigureOptions("enable-xft"		, self.options.enable_xft)
			self.setConfigureOptions("enable-xdbe"		, self.options.enable_xdbe)
			self.setConfigureOptions("enable-xfixes"	, self.options.enable_xfixes)
			self.setConfigureOptions("enable-xcursor"	, self.options.enable_xcursor)
			self.setConfigureOptions("enable-xrender"	, self.options.enable_xrender)

			self.configure_options += " --enable-debug=%s" % ("yes" if self.settings.build_type == "Debug" else "no")
			if(self.options.disable_largefile):
				self.configure_options += " --disable-largefile"

			complete_configure_cmd = change_build_dir + configure_cmd + self.configure_options
			self.output.info("Configure: " + complete_configure_cmd)
			self.run(complete_configure_cmd)

			complete_make_cmd = change_build_dir + make_cmd
			self.output.info("Make: " + complete_make_cmd)
			self.run(complete_make_cmd)

	def build_windows(self):
		cmake = CMake(self.settings)
		self.output.info(self.conanfile_directory)
		cmake_configure_cmd = "cmake %s/fltk %s" % (self.conanfile_directory, cmake.command_line)
		self.run(cmake_configure_cmd)

		cmake_build_extra_cmd = " -- /maxcpucount:%d" % (tools.cpu_count())
		cmake_build_cmd = "cmake --build . %s %s" % (cmake.build_config, cmake_build_extra_cmd)

		self.run(cmake_build_cmd)

	def build(self):
		if self.settings.os == "Windows":
			self.build_windows()
		else: # Linux and Mac
			self.build_unix()

	def package(self):
		if self.settings.os == "Windows":
			self.copy("*.h", dst="include/FL", src="fltk/FL/")
			self.copy("*.h*", dst="include/FL", src="FL")
			self.copy("*.lib", dst="lib", src="lib")
		else:
			self.copy("*.h*", dst="include", src="fltk")
			self.copy("*.H*", dst="include", src="fltk")
			self.copy("*.a", dst="", src="fltk")

	def package_info(self):
		if self.settings.os == "Windows" and self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
			self.cpp_info.libs.append("fltkd")
			self.cpp_info.libs.append("fltk_formsd")
			if(self.options.enable_gl):
				self.cpp_info.libs.append("fltk_gld")
			self.cpp_info.libs.append("fltk_imagesd")
			self.cpp_info.libs.append("fltk_jpegd")
			self.cpp_info.libs.append("fltk_pngd")
			self.cpp_info.libs.append("fltk_zd")
		else:
			self.cpp_info.libs.append("fltk")
			self.cpp_info.libs.append("fltk_forms")
			#if(self.options.enable_gl):
#				self.cpp_info.libs.append("fltk_gl")
			self.cpp_info.libs.append("fltk_images")
			self.cpp_info.libs.append("fltk_jpeg")
			self.cpp_info.libs.append("fltk_png")
			self.cpp_info.libs.append("fltk_z")	
		if self.settings.os == "Macos":
			linkFlags = ["-framework Foundation", "-framework CoreGraphics", "-framework CoreText", "-framework AppKit", "-w"] 
			self.cpp_info.sharedlinkflags = linkFlags
			self.cpp_info.exelinkflags = linkFlags
		if self.settings.os == "Linux":
			#TODO: install dependencies:  sudo apt-get install -y libx11-dev libpng-dev libxft-dev libxext-dev libxfixes-dev libxinerama-dev libxcursor-dev libxrender-dev			
			#TODO: implement conan projects of these libraries
			self.cpp_info.libs.extend(["Xcursor", "Xfixes", "Xext", "Xft", "fontconfig", "Xinerama", "dl", "m", "X11", "Xrender", "pthread"])