%define api %(echo %{version} |cut -d. -f1)
%define major %api
%define beta %{nil}

%define qtwebchannel %mklibname qt%{api}webchannel %{major}
%define qtwebchanneld %mklibname qt%{api}webchannel -d
%define qtwebchannel_p_d %mklibname qt%{api}webchannel-private -d

%define _qt5_prefix %{_libdir}/qt%{api}

Summary:	Qt %{api} WebChannel library
Group:		Development/KDE and Qt
License:	LGPLv2 with exceptions or GPLv3 with exceptions and GFDL
URL:		https://www.qt.io
Name:		qt5-qtwebchannel
Version:	5.15.15
%if "%{beta}" != ""
Release:	0.%{beta}.1
%define qttarballdir qtwebchannel-everywhere-src-%{version}-%{beta}
Source0:	http://download.qt.io/development_releases/qt/%(echo %{version}|cut -d. -f1-2)/%{version}-%{beta}/submodules/%{qttarballdir}.tar.xz
%else
Release:	1
%define qttarballdir qtwebchannel-everywhere-opensource-src-%{version}
Source0:	http://download.qt.io/official_releases/qt/%(echo %{version}|cut -d. -f1-2)/%{version}/submodules/%{qttarballdir}.tar.xz
%endif
Source1000:	%{name}.rpmlintrc

# From KDE https://invent.kde.org/qt/qt/qtwebchannel -b kde/5.15
%(P=1001; cd %{_sourcedir}; for i in [0-9][0-9][0-9][0-9]-*.patch; do echo -e "Patch$P:\t$i"; P=$((P+1)); done)

BuildRequires:	qmake5
BuildRequires:	pkgconfig(Qt5Core) >= %{version}
BuildRequires:	pkgconfig(Qt5Quick) >= %{version}
# For the Provides: generator
BuildRequires:	cmake >= 3.11.0-1

%description
Qt %{api} WebChannel library,  a library for communication between
HTML/JavaScript and Qt/QML objects.

%files
%{_qt5_prefix}/qml/QtWebChannel
%{_qt5_exampledir}/webchannel

#------------------------------------------------------------------------------

%package -n %{qtwebchannel}
Summary:	Qt%{api} Component Library
Group:		System/Libraries

%description -n %{qtwebchannel}
Qt%{api} Component Library.

%files -n %{qtwebchannel}
%{_qt5_libdir}/libQt5WebChannel.so.%{major}*

#------------------------------------------------------------------------------

%package -n %{qtwebchanneld}
Summary:	Devel files needed to build apps based on %{name}
Group:		Development/KDE and Qt
Requires:	%{qtwebchannel} = %{version}

%description -n %{qtwebchanneld}
Devel files needed to build apps based on %{name}.

%files -n %{qtwebchanneld}
%{_qt5_libdir}/libQt5WebChannel.so
%{_qt5_libdir}/libQt5WebChannel.prl
%{_qt5_libdir}/pkgconfig/Qt5WebChannel.pc
%{_qt5_includedir}/QtWebChannel
%exclude %{_qt5_includedir}/QtWebChannel/%{version}
%{_qt5_prefix}/mkspecs/modules/qt_lib_webchannel.pri
%{_qt5_libdir}/cmake/Qt5WebChannel

#------------------------------------------------------------------------------

%package -n %{qtwebchannel_p_d}
Summary:	Devel files needed to build apps based on %{name}
Group:		Development/KDE and Qt
Requires:	%{qtwebchanneld} = %{version}
Requires:	pkgconfig(Qt5Core)  = %{version}
Requires:	qt5-qtscript-private-devel = %{version}
Provides:	qt5-qtwebchannel-private-devel = %{version}

%description -n %{qtwebchannel_p_d}
Devel files needed to build apps based on %{name}.

%files -n %{qtwebchannel_p_d}
%{_qt5_includedir}/QtWebChannel/%{version}
%{_qt5_prefix}/mkspecs/modules/qt_lib_webchannel_private.pri

#------------------------------------------------------------------------------

%prep
%autosetup -n %(echo %qttarballdir|sed -e 's,-opensource,,') -p1
%{_qt5_prefix}/bin/syncqt.pl -version %{version}

%build
%qmake_qt5
%make_build

#------------------------------------------------------------------------------
%install
%make_install INSTALL_ROOT=%{buildroot}

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
cd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
cd -
