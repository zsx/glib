/*
 * Copyright (C) 2008 Tor Lillqvist
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; see the file COPYING.LIB.txt.  If
 * not, write to the Free Software Foundation, Inc., 51 Franklin
 * Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include <windows.h>

#include "libintl.h"

int _nl_msg_cat_cntr;		/* So that configury knows it actually
				 * is GNU gettext
				 */

static char * (*p_gettext) (const char *msgid);

static char * (*p_dgettext) (const char *domainname,
			     const char *msgid);

static char * (*p_dcgettext) (const char *domainname,
			      const char *msgid,
			      int         category);

static char * (*p_ngettext) (const char       *msgid1,
			     const char       *msgid2,
			     unsigned long int n);

static char * (*p_dngettext) (const char       *domainname,
			      const char       *msgid1,
			      const char       *msgid2,
			      unsigned long int n);

static char * (*p_dcngettext) (const char       *domainname,
			       const char       *msgid1,
			       const char       *msgid2,
			       unsigned long int n,
			       int               category);

static char * (*p_textdomain) (const char *domainname);

static char * (*p_bindtextdomain) (const char *domainname,
				   const char *dirname);

static char * (*p_bind_textdomain_codeset) (const char *domainname,
					    const char *codeset);

static int
use_intl_dll (HMODULE dll)
{
#define LOOKUP(fn) p_##fn = (void *) GetProcAddress (dll, #fn); if (p_##fn == NULL) return 0

  LOOKUP (gettext);
  LOOKUP (dgettext);
  LOOKUP (dcgettext);
  LOOKUP (ngettext);
  LOOKUP (dngettext);
  LOOKUP (dcngettext);
  LOOKUP (textdomain);
  LOOKUP (bindtextdomain);
  LOOKUP (bind_textdomain_codeset);
  
#undef LOOKUP

  return 1;
}

#define DUMMY(fn, parlist, retval)		\
static char *					\
dummy_##fn parlist				\
{						\
  return (char *) (retval);			\
}

DUMMY (gettext, (const char *msgid), msgid)

DUMMY (dgettext, 
       (const char *domainname,
	const char *msgid),
       msgid)

DUMMY (dcgettext,
       (const char *domainname,
	const char *msgid,
	int         category),
       msgid)

DUMMY (ngettext,
       (const char       *msgid1,
	const char       *msgid2,
	unsigned long int n),
       n == 1 ? msgid1 : msgid2)

DUMMY (dngettext,
       (const char       *domainname,
	const char       *msgid1,
	const char       *msgid2,
	unsigned long int n),
       n == 1 ? msgid1 : msgid2)

DUMMY (dcngettext,
       (const char       *domainname,
	const char       *msgid1,
	const char       *msgid2,
	unsigned long int n,
	int               category),
       n == 1 ? msgid1 : msgid2)

DUMMY (textdomain,
       (const char *domainname),
       domainname)

DUMMY (bindtextdomain,
       (const char *domainname,
	const char *dirname),
       domainname)

DUMMY (bind_textdomain_codeset,
       (const char *domainname,
	const char *codeset),
       domainname)		/* ?? */

#undef DUMMY

static void
use_dummy (void)
{
#define USE_DUMMY(fn) p_##fn = dummy_##fn

  USE_DUMMY (gettext);
  USE_DUMMY (dgettext);
  USE_DUMMY (dcgettext);
  USE_DUMMY (ngettext);
  USE_DUMMY (dngettext);
  USE_DUMMY (dcngettext);
  USE_DUMMY (textdomain);
  USE_DUMMY (bindtextdomain);
  USE_DUMMY (bind_textdomain_codeset);
  
#undef USE_DUMMY

}

static void
setup (void)
{
  static int beenhere = 0;

  if (!beenhere)
    {
      HMODULE intl_dll = LoadLibrary ("intl.dll");

      if (intl_dll != NULL &&
	  use_intl_dll (intl_dll))
	;
      else
	use_dummy ();

      beenhere = 1;
    }
}

char *
gettext (const char *msgid)
{
  setup ();
  return p_gettext (msgid);
}

char *
dgettext (const char *domainname,
	  const char *msgid)
{
  setup ();
  return p_dgettext (domainname, msgid);
}

char *
dcgettext (const char *domainname,
	   const char *msgid,
	   int         category)
{
  setup ();
  return p_dcgettext (domainname, msgid, category);
}

char *
ngettext (const char       *msgid1,
	  const char       *msgid2,
	  unsigned long int n)
{
  setup ();
  return p_ngettext (msgid1, msgid2, n);
}
  
char *
dngettext (const char       *domainname,
	   const char       *msgid1,
	   const char       *msgid2,
	   unsigned long int n)
{
  setup ();
  return p_dngettext (domainname, msgid1, msgid2, n);
}

char *
dcngettext (const char       *domainname,
	    const char       *msgid1,
	    const char       *msgid2,
	    unsigned long int n,
	    int               category)
{
  setup ();
  return p_dcngettext (domainname, msgid1, msgid2, n, category);
}

char *
textdomain (const char *domainname)
{
  setup ();
  return p_textdomain (domainname);
}

char *
bindtextdomain (const char *domainname,
		const char *dirname)
{
  setup ();
  return p_bindtextdomain (domainname, dirname);
}

char *
bind_textdomain_codeset (const char *domainname,
			 const char *codeset)
{
  setup ();
  return p_bind_textdomain_codeset (domainname, codeset);
}

#ifdef __cplusplus
}
#endif
