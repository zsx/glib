#!/usr/bin/env python
# encoding: utf-8
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'github'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github.autoconf.alloca import *
from github.autoconf.misc import *
from github.autoconf.compute_int import *
from github.autoconf.endian import *
from github.autoconf.printf_unix98 import *
from github.autoconf.sizeof import *
from github.autoconf.stdc_headers import *
from github.autoconf.vsnprintf_c99 import *
from github.misc import *
from github.platinfo import PlatInfo
