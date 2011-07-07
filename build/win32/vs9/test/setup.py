#!/usr/bin/python
# vim: encoding=utf-8
#expand *.in files
#this script is only intended for building from git, not for building from the released tarball, which already includes all necessary files
import os
import sys
import re
import string
import subprocess
import optparse
import uuid

def read_vars_from_AM(path, vars = {}, conds = {}, filters = None):
    '''
    path: path to the Makefile.am
    vars: predefined variables
    conds: condition variables for Makefile
    filters: if None, all variables defined are returned,
             otherwise, it is a list contains that variables should be returned 
    '''
    cur_vars = vars.copy()
    RE_AM_VAR_REF = re.compile(r'\$\((\w+?)\)')
    RE_AM_VAR = re.compile(r'^\s*(\w+)\s*=(.*)$')
    RE_AM_VAR_APPEND = re.compile(r'^\s*(\w+)\s*\+=(.*)$')
    RE_AM_INCLUDE = re.compile(r'^\s*include\s+(\w+)')
    RE_AM_CONTINUING = re.compile(r'\\\s*$')
    RE_AM_IF = re.compile(r'^\s*if\s+(\w+)')
    RE_AM_ELSE = re.compile(r'^\s*else')
    RE_AM_ENDIF = re.compile(r'^\s*endif')
    def am_eval(cont):
        return RE_AM_VAR_REF.sub(lambda x: cur_vars.get(x.group(1), ''), cont)
    with open(path, 'r') as f:
        contents = f.readlines()
    #combine continuing lines
    i = 0
    ncont = []
    while i < len(contents):
        line = contents[i]
        if RE_AM_CONTINUING.search(line):
            line = RE_AM_CONTINUING.sub('', line)
            j = i + 1
            while j < len(contents) and RE_AM_CONTINUING.search(contents[j]):
                line += RE_AM_CONTINUING.sub('', contents[j])
                j += 1
            else:
                if j < len(contents):
                    line += contents[j]
            i = j
        else:
            i += 1
        ncont.append(line)

    #include, var define, var evaluation
    i = -1
    skip = False
    oldskip = []
    while i < len(ncont) - 1:
        i += 1
        line = ncont[i]
        mo = RE_AM_IF.search(line)
        if mo:
            oldskip.append(skip)
            skip = False if mo.group(1) in conds and conds[mo.group(1)] \
                         else True
            continue
        mo = RE_AM_ELSE.search(line)
        if mo:
            skip = not skip
            continue
        mo = RE_AM_ENDIF.search(line)
        if mo:
            skip = oldskip.pop()
            continue
        if not skip:
            mo = RE_AM_INCLUDE.search(line)
            if mo:
                cur_vars.update(read_vars_from_AM(am_eval(mo.group(1)), cur_vars, conds, None))
                continue
            mo = RE_AM_VAR.search(line)
            if mo:
                cur_vars[mo.group(1)] = am_eval(mo.group(2).strip())
                continue
            mo = RE_AM_VAR_APPEND.search(line)
            if mo:
                cur_vars[mo.group(1)] +=  " " + am_eval(mo.group(2).strip())
                continue
    
    #filter:
    if filters != None:
        ret = {}
        for i in filters:
            ret[i] = cur_vars.get(i, '')
        return ret
    else:
        return cur_vars

def generate_vcproject(proj_tplt, subs):
    RE_VAR = re.compile(r'@(\w+?)@')
    def vc_subs(mo):
        if mo.group(1) in subs:
            return subs[mo.group(1)]
        elif mo.group(1) == 'GUID':
            return str(uuid.uuid4()).upper()
        else:
            return ''
    return RE_VAR.sub(vc_subs, proj_tplt)

def main(argv):
    def parent_dir(path):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        return os.path.split(path)[0]
    parser = optparse.OptionParser()
    parser.add_option('-p', '--glib-prefix', dest='prefix', metavar='PATH', default='../../../../../../vs9/Win32', action='store', help='path to the prefix dir of installed glib')
    parser.add_option('-s', '--source-prefix', dest='srcroot', metavar='PATH', default=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')), action='store', help='path to the root directory of the source tree')
    opt, args = parser.parse_args(argv)
    slndir = os.path.join(opt.srcroot, 'build', 'win32', 'vs9', 'test')
    testdir = os.path.join(opt.srcroot, 'glib', 'tests')
    vars = read_vars_from_AM(os.path.join(testdir, 'Makefile.am'),
                             vars={'top_srcdir': opt.srcroot,
                                   'TEST_PROGS': "",
                                   'EXTRA_DIST': ""},
                             conds={'OS_WIN32': True})
    with open('template.vcproj', 'r') as tplt:
        proj_tplt = tplt.read()
    with open('glibtest.sln', 'w') as sln:
        sln.write('''Microsoft Visual Studio Solution File, Format Version 10.00
# Visual Studio 2008
''')
        projects = ''
        gsection = ''
        for t in vars['TEST_PROGS'].split():
            proj_uuid = str(uuid.uuid4()).upper()
            sources = vars.get(t + '_SOURCES', t + '.c').split()
            sources_elems = ''
            for s in sources:
                sources_elems += '''\t
			<File RelativePath="%s\\%s" />\n''' % (os.path.relpath(testdir, slndir), s)
            with open(t + '.vcproj', 'w') as proj:
                subs = {'NAME': t,
                        'PROJECT_GUID': proj_uuid,
                        'ROOT_NAME_SPACE': t + 'NameSpace',
                        'SOURCES': sources_elems
                        }
                proj.write(generate_vcproject(proj_tplt, subs))
                projects += 'Project("{%s}") = "%s", "%s.vcproj", "{%s}" \nEndProject\n' % (str(uuid.uuid4()).upper(), t, t, proj_uuid)
                gsection += string.Template('''
		{$GUID}.Debug|Win32.ActiveCfg = Debug|Win32
		{$GUID}.Debug|Win32.Build.0 = Debug|Win32
		{$GUID}.Debug|x64.ActiveCfg = Debug|x64
		{$GUID}.Debug|x64.Build.0 = Debug|x64
		{$GUID}.Release|Win32.ActiveCfg = Release|Win32
		{$GUID}.Release|Win32.Build.0 = Release|Win32
		{$GUID}.Release|x64.ActiveCfg = Release|x64
		{$GUID}.Release|x64.Build.0 = Release|x64
                ''').substitute(GUID=proj_uuid)
        sln.write(projects)
        sln.write('''Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Win32 = Debug|Win32
		Release|Win32 = Release|Win32
		Debug|Win64 = Debug|Win64
		Release|Win64 = Release|Win64
	EndGlobalSection
''')
	sln.write('GlobalSection(ProjectConfigurationPlatforms) = postSolution\n')
        sln.write(gsection)
	sln.write('EndGlobalSection')
        sln.write('''
    GlobalSection(SolutionProperties) = preSolution
        HideSolutionNode = FALSE
    EndGlobalSection
EndGlobal
''')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
