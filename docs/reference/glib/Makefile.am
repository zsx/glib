## Process this file with automake to produce Makefile.in
include $(top_srcdir)/Makefile.decl

AUTOMAKE_OPTIONS = 1.6

# The name of the module.
DOC_MODULE=glib

# The top-level SGML file.
DOC_MAIN_SGML_FILE=glib-docs.sgml

# The directory containing the source code. Relative to $(srcdir)
DOC_SOURCE_DIR=../../../glib ../../../gmodule

# Extra options to supply to gtkdoc-scan
SCAN_OPTIONS=--deprecated-guards="G_DISABLE_DEPRECATED" --ignore-decorators="GLIB_VAR"

# Extra options to supply to gtkdoc-mkdb
MKDB_OPTIONS=--sgml-mode --output-format=xml --name-space=g

# Used for dependencies
HFILE_GLOB=$(addprefix $(top_srcdir)/glib/,$(shell cat $(top_builddir)/glib/glib-public-headers.txt)) $(top_srcdir)/gmodule/*.h
CFILE_GLOB=$(top_srcdir)/glib/*.c $(top_srcdir)/gmodule/*.c

# Images to copy into HTML directory
HTML_IMAGES =  				\
	file-name-encodings.png		\
	mainloop-states.gif

# Extra SGML files that are included by $(DOC_MAIN_SGML_FILE)
content_files =				\
	cross.sgml			\
	running.sgml			\
	building.sgml			\
	changes.sgml			\
	compiling.sgml			\
	resources.sgml			\
	regex-syntax.sgml		\
	version.xml			\
	glib-gettextize.xml		\
	gtester.xml			\
	gtester-report.xml		\
	gvariant-varargs.xml		\
	gvariant-text.xml

# Extra options to supply to gtkdoc-fixref
FIXXREF_OPTIONS=

# include common portion ...
include $(top_srcdir)/gtk-doc.make

# Other files to distribute
EXTRA_DIST +=				\
	file-name-encodings.png		\
	file-name-encodings.sxd		\
	mainloop-states.fig		\
	mainloop-states.png		\
	mainloop-states.eps		\
	version.xml.in

########################################################################

man_MANS =		  	\
	glib-gettextize.1 	\
	gtester.1		\
	gtester-report.1

if ENABLE_MAN

.xml.1:
	@XSLTPROC@ -nonet http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl $<

dist-local-check-mans-enabled:
	if grep "Man generation disabled" $(man_MANS) >/dev/null; then $(RM) $(man_MANS); fi

else

$(man_MANS):
	echo Man generation disabled.  Creating dummy $@.  Configure with --enable-man to enable it.
	echo Man generation disabled.  Remove this file, configure with --enable-man, and rebuild > $@

dist-local-check-mans-enabled:
	echo "*** --enable-man must be used in order to make dist"
	false

endif

MAINTAINERCLEANFILES = $(man_MANS) $(BUILT_SOURCES)

EXTRA_DIST += $(man_MANS)

dist-hook-local: dist-local-check-mans-enabled glib-docs-clean all-local

glib-docs-clean: clean
	cd $(srcdir) && rm -rf xml html
