This is a trivial minimal library intended to act as a proxy for a
dynamically loaded optional intl.dll (the core DLL of GNU
gettext-runtime). It is relevant on Windows only, as far as I can see,
as on Linux you have gettext functionality already in the C
library. If somebody wants to enhance this to work on non-Windows, for
instance embedded cases, feel free to send in patches.

It is to be used when building other software that want to use i18n
features of (GNU) gettext (as ported to Windows), but for which one
wants to be able to decide only at package (installer) construction
time whether to actually support i18n or not. In the negative case,
one wants to avoid having to ship the gettext DLL (intl.dll) at all.

Tor Lillqvist <tml@iki.fi>, March 2008
