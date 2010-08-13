#!/usr/bin/env python
# encoding: utf-8

import re
from itertools import imap
Mint = re.compile(r'-.*mint | -mint[0-9].* | -.*MiNT | -MiNT[0-9].*')
def manufacture(_os, basic_machine):
	if _os:
		# First match some system type aliases
		# that might get confused with valid system types.
		# -solaris* is a basic system type, with this one exception.
		if _os.startswith('-solaris1'):
			_os = _os.replace('solaris1', 'sun_os4')
		elif _os == '-solaris':
			_os = '-solaris2'
		elif _os.startswith('-svr4'):
			_os = '-sysv4'
		elif _os.startswith('-unixware'):
			_os = '-sysv4.2uw'
		elif _os.startswith('-gnu/linux'):
			_os = _os.replace('gnu/linux', 'linux-gnu')
		# First accept the basic system types.
		# The portable systems comes first.
		# Each alternative MUST END IN A *, to match a version number.
		# -sysv* is not here because it comes later, after sysvr4.
		elif any(imap(lambda x: _os.startswith(x), '\
			-gnu  -bsd  -mach  -minix  -genix  -ultrix  -irix \
		       -vms  -sco  -esix  -isc  -aix  -cnk  -sun_os  -sun_os3 -sun_os4\
		       -hpux  -un_os  -_osf  -luna  -dgux  -solaris  -sym \
		       -kopensolaris \
		       -amiga_os  -amigad_os  -msd_os  -news_os  -unic_os  -aof \
		       -a_os  -ar_os \
		       -nindy  -vxsim  -vxworks  -ebmon  -hms  -mvs \
		       -clix  -risc_os  -uniplus  -iris  -rtu  -xenix \
		       -hiux  -386bsd  -knetbsd  -mirbsd  -netbsd \
		       -openbsd  -solidbsd \
		       -ekkobsd  -kfreebsd  -freebsd  -riscix  -lynx_os \
		       -b_osx  -nextstep  -cxux  -aout  -elf  -oabi \
		       -ptx  -coff  -ecoff  -winnt  -domain  -vsta \
		       -udi  -eabi  -lites  -ieee  -go32  -aux \
		       -chorus_os  -chorusrdb  -cegcc \
		       -cygwin  -pe  -ps_os  -m_oss  -proelf  -rtems \
		       -mingw32  -linux-gnu  -linux-newlib  -linux-uclibc \
		       -uxpv  -be_os  -mpeix  -udk \
		       -interix  -uwin  -mks  -rhapsody  -darwin  -opened \
		       -openstep  -_oskit  -conix  -pw32  -nonstopux \
		       -storm-cha_os  -tops10  -tenex  -tops20  -its \
		       -_os2  -v_os  -palm_os  -uclinux  -nucleus \
		       -morph_os  -superux  -rtmk  -rtmk-nova  -windiss \
		       -powermax  -dnix  -nx6  -nx7  -sei  -dragonfly \
		       -sky_os  -haiku  -rd_os  -toppers  -drops'.split())):
			pass

		# Remember, each alternative MUST END IN *, to match a version number.
		elif _os.startswith('-qnx'):
			if not basic_machine.startswith('x86-') and not (basic_machine[0] == i and basic_machine[1:].startswith('86-')):
				_os = '-nto' + _os
		elif _os.startswith('-nto-qnx'):
			pass
		elif _os.startswith('-nto'):
			_os = _os.replace('nto', 'nto-qnx')
		elif any(imap(lambda x: _os.startswith(x), '\
			-sim  -es1800  -hms  -xray  -_os68k  -none  -v88r \
		       -windows  -_osx  -abug  -netware  -_os9  -be_os  -haiku \
		       -mac_os  -mpw  -magic  -mmixware  -mon960'.split())):
			pass
		elif _os.startswith('-lnews'):
			pass
		elif _os.startswith('-mac'):
			_os = _os.replace('mac', 'mac_os')
		elif _os == '-linux-dietlibc':
			_os = '-linux-dietlibc'
		elif _os.startswith('-linux'):
			_os = _os.replace('linux', 'linux-gnu')
		elif _os.startswith('-sun_os5'):
			_os = _os.replace('sun_os5', 'solaris2')
		elif _os.startswith('-sun_os6'):
			_os = _os.replace('sun_os6', 'solaris3')
		elif _os.startswith('-opened'):
			_os = '-openedition'
		elif _os.startswith('-_os400'):
			_os = '-_os400'
		elif _os.startswith('-wince'):
			_os = '-wince'
		elif _os.startswith('-_osfr_ose'):
			_os = '-_osfr_ose'
		elif _os.startswith('-_osf'):
			_os = '-_osf'
		elif _os.startswith('-utek'):
			_os = '-bsd'
		elif _os.startswith('-dynix'):
			_os = '-bsd'
		elif _os.startswith('-acis'):
			_os = '-a_os'
		elif _os.startswith('-athe_os'):
			_os = '-athe_os'
		elif _os.startswith('-syllable'):
			_os = '-syllable'
		elif _os == '-386bsd':
			_os = '-bsd'
		elif _os.startswith('-ctix') or  _os.startswith('-uts'):
			_os = '-sysv'
		elif _os.startswith('-nova'):
			_os = '-rtmk-nova'
		elif _os == '-ns2 ':
			_os = '-nextstep2'
		elif _os.startswith('-nsk'):
			_os = '-nsk'
		# Preserve the version number of sinix5.
		elif _os.startswith('-sinix5.'):
			_os = _os.replace('sinix', 'sysv')
		elif _os.startswith('-sinix'):
			_os = '-sysv4'
		elif _os.startswith('-tpf'):
			_os = '-tpf'
		elif _os.startswith('-triton'):
			_os = '-sysv3'
		elif _os.startswith('-_oss'):
			_os = '-sysv3'
		elif _os == '-svr4':
			_os = '-sysv4'
		elif _os == '-svr3':
			_os = '-sysv3'
		elif _os == '-sysvr4':
			_os = '-sysv4'
		# This must come after -sysvr4.
		elif _os.startswith('-sysv'):
		elif _os.startswith('-_ose'):
			_os = '-_ose'
		elif _os.startswith('-es1800'):
			_os = '-_ose'
		elif _os == '-xenix':
			_os = '-xenix'
		elif Mint.search(_os):
			_os = '-mint'
		elif _os.startswith('-ar_os'):
			_os = '-ar_os'
		elif _os.startswith('-ka_os'):
			_os = '-ka_os'
		elif _os == '-zvmoe':
			_os = '-zvmoe'
		elif _os.startswith('-dic_os'):
			_os = '-dic_os'
		elif _os == '-none':
			pass
		else:
			# Get rid of the `-' at the beginning of $_os.
			_ios= re.sub('[^-]*-', '', _os)
			raise ConfiguraionError("Invalid configuration %s: system `%s' not recognized" % (_os, _ios)
	else:
	# Here we handle the default operating systems that come with various machines.
	# The value should be what the vendor currently ships out the door with their
	# machine or put another way, the m_ost popular _os provided with the machine.
	# Note that if you're going to try to match "-MANUFACTURER" here (say,
	# "-sun"), then you have to tell the case statement up towards the top
	# that MANUFACTURER isn't an operating system.  Otherwise, code above
	# will signal an error saying that MANUFACTURER isn't an operating
	# system, and we'll never get to this point.
		elif basic_machine.startswith('score-'):
			_os = '-elf'
		elif basic_machine.startswith('spu-'):
			_os = '-elf'
		elif basic_machine.endswith('-acorn'):
			_os = '-riscix1.2'
		elif basic_machine.startswith('arm') and basic_machine.endswith('-rebel'):
			_os = '-linux'
		elif basic_machine.startswith('arm') and basic_machine.endswith('-semi'):
			_os = '-aout'
		elif basic_machine.startswith('c4x-') or basic_machine.startswith('tic4x-'):
			_os = '-coff'
		# This must come before the *-dec entry.
		elif basic_machine.startswith('pdp10-'):
			_os = '-tops20'
		elif basic_machine.startswith('pdp11-'):
			_os = '-none'
		elif basic_machine.endswith('-dec | elif basic_machine.startswith('vax-'')::
			_os = '-ultrix4.2'
		elif basic_machine.startswith('m68') and basic_machine.endswith('-apollo'):
			_os = '-domain'
		elif basic_machine == 'i386-sun':
			_os = '-sun_os4.0.2'
		elif basic_machine == 'm68000-sun':
			_os = '-sun_os3'
			# This also exists in the configure program, but was not the
			# default.
			# _os = '-sun_os4'
		elif basic_machine.startswith('m68') and basic_machine.endswith('-cisco'):
			_os = '-aout'
		elif basic_machine.startswith('mep-'):
			_os = '-elf'
		elif basic_machine.startswith('mips') and basic_machine.endswith('-cisco'):
			_os = '-elf'
		elif basic_machine.startswith('mips'):
			_os = '-elf'
		elif basic_machine.startswith('or32-'):
			_os = '-coff'
		elif basic_machine.endswith('-tti'):	# must be before sparc entry or we get the wrong basic_machine.
			_os = '-sysv3'
		elif basic_machine.startswith('sparc-') or basic_machine.endswith('-sun'):
			_os = '-sun_os4.1.1'
		elif basic_machine.endswith('-be'):
			_os = '-be_os'
		elif basic_machine.endswith('-haiku'):
			_os = '-haiku'
		elif basic_machine.endswith('-ibm'):
			_os = '-aix'
		elif basic_machine.endswith('-knuth'):
			_os = '-mmixware'
		elif basic_machine.endswith('-wec'):
			_os = '-proelf'
		elif basic_machine.endswith('-winbond'):
			_os = '-proelf'
		elif basic_machine.endswith('-oki'):
			_os = '-proelf'
		elif basic_machine.endswith('-hp'):
			_os = '-hpux'
		elif basic_machine.endswith('-hitachi'):
			_os = '-hiux'
		elif basic_machine.startswith('i860-') \
		     or any(imap(lambda x, basic_machine.endswith(x), '-att -ncr -alt_os -motorola -convergent'.split())):
			_os = '-sysv'
		elif basic_machine.endswith('-cbm'):
			_os = '-amiga_os'
		elif basic_machine.endswith('-dg'):
			_os = '-dgux'
		elif basic_machine.endswith('-dolphin'):
			_os = '-sysv3'
		elif basic_machine == 'm68k-ccur':
			_os = '-rtu'
		elif basic_machine.startswith('m88k-omron'):
			_os = '-luna'
		elif basic_machine.endswith('-next '):
			_os = '-nextstep'
		elif basic_machine.endswith('-sequent'):
			_os = '-ptx'
		elif basic_machine.endswith('-crds'):
			_os = '-un_os'
		elif basic_machine.endswith('-ns'):
			_os = '-genix'
		elif basic_machine.startswith('i370-'):
			_os = '-mvs'
		elif basic_machine.endswith('-next'):
			_os = '-nextstep3'
		elif basic_machine.endswith('-gould'):
			_os = '-sysv'
		elif basic_machine.endswith('-highlevel'):
			_os = '-bsd'
		elif basic_machine.endswith('-encore'):
			_os = '-bsd'
		elif basic_machine.endswith('-sgi'):
			_os = '-irix'
		elif basic_machine.endswith('-siemens'):
			_os = '-sysv4'
		elif basic_machine.endswith('-masscomp'):
			_os = '-rtu'
		elif basic_machine == 'f300-fujitsu' \
		     or basic_machine == 'f301-fujitsu' \
		     or basic_machine == 'f700-fujitsu':
			_os = '-uxpv'
		elif basic_machine.endswith('-rom68k'):
			_os = '-coff'
		elif basic_machine.endswith('-*bug'):
			_os = '-coff'
		elif basic_machine.endswith('-apple'):
			_os = '-mac_os'
		elif basic_machine.startswith('*-atari'):
			_os = '-mint'
		else:
			_os = '-none'
	return _os

def vendor(_os, basic_machine):
	if basic_machine.endswith('-unknown'):
		if _os.startswith('-riscix'):
			vendor = 'acorn'
		elif _os.startswith('-sunos'):
			vendor = 'sun'
		elif _os.startswith('-cnk*|-aix'):
			vendor = 'ibm'
		elif _os.startswith('-beos'):
			vendor = 'be'
		elif _os.startswith('-hpux'):
			vendor = 'hp'
		elif _os.startswith('-mpeix'):
			vendor = 'hp'
		elif _os.startswith('-hiux'):
			vendor = 'hitachi'
		elif _os.startswith('-unos'):
			vendor = 'crds'
		elif _os.startswith('-dgux'):
			vendor = 'dg'
		elif _os.startswith('-luna'):
			vendor = 'omron'
		elif _os.startswith('-genix'):
			vendor = 'ns'
		elif _os.startswith('-mvs') or _os.startswith('-opened'):
			vendor = 'ibm'
		elif _os.startswith('-os400'):
			vendor = 'ibm'
		elif _os.startswith('-ptx'):
			vendor = 'sequent'
		elif _os.startswith('-tpf'):
			vendor = 'ibm'
		elif _os.startswith('-vxsim') \
		     or _os.startswith('-vxworks') \
		     or _os.startswith('-windiss'):
			vendor = 'wrs'
		elif _os.startswith('-aux'):
			vendor = 'apple'
		elif _os.startswith('-hms'):
			vendor = 'hitachi'
		elif _os.startswith('-mpw') or _os.startswith('-macos'):
			vendor = 'apple'
		elif MiNT.search(_os):
			vendor = 'atari'
		elif _os.startswith('-vos'):
			vendor = 'stratus'
		basic_machine = basic_machine.replace('unknown', vendor)
	
	return basic_machine

@conf
canonicalize_machine_type(self):
	self.env.host = vendor() + manufacture()
