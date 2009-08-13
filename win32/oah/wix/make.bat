@echo off
set GLIB_RELEASE_PATH=%~dp0\..\Win32\Release
set MAJORMINOR=2.0
%OAH_INSTALLED_PATH%bin\pkg-config --modversion %GLIB_RELEASE_PATH%\lib\pkgconfig\glib-%MAJORMINOR%.pc > glibver.tmp || goto error
set /P GLIBVER= < glibver.tmp
del glibver.tmp

nmake /nologo version=%GLIBVER% api_version=%MAJORMINOR% release_path=%GLIB_RELEASE_PATH% %*

goto:eof
:error
del glibver.tmp
echo Couldn't start build process... are pkg-config in your PATH and/or have you compiled GLib.sln with OAH_BUILD_OUTPUT cleared!??