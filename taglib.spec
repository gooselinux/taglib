
# Fedora cvs admin requests for taglib: http://bugzilla.redhat.com/418271

%bcond_without tests

%if %{with tests}
%global buildtests -DBUILD_TESTS=ON
%endif

%bcond_without doc
%global apidocdir __api-doc_fedora

Name:       taglib	
Version:    1.6.1
Release:    1.1%{?dist}
Summary:    Audio Meta-Data Library

Group: 	    System Environment/Libraries
License:    LGPLv2
URL:        http://developer.kde.org/~wheeler/taglib.html
Source0:    http://developer.kde.org/~wheeler/files/src/taglib-%{version}.tar.gz
#Source0:    taglib-%{svn}.tar.gz
# The svn tarball is generated with the following script
Source1:    taglib-svn.sh
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# http://bugzilla.redhat.com/343241
# try 1, use pkg-config
Patch1:     taglib-1.5b1-multilib.patch 
# try 2, kiss omit -L%_libdir
Patch2:     taglib-1.5rc1-multilib.patch

BuildRequires: cmake
BuildRequires: pkgconfig
BuildRequires: zlib-devel
%if %{with tests}
BuildRequires: cppunit-devel
%endif
%if %{with doc}
BuildRequires: doxygen
BuildRequires: graphviz
%endif


%description
TagLib is a library for reading and editing the meta-data of several
popular audio formats. Currently it supports both ID3v1 and ID3v2 for MP3
files, Ogg Vorbis comments and ID3 tags and Vorbis comments in FLAC, MPC,
Speex, WavPack, TrueAudio files, as well as APE Tags.


%if %{with doc}
%package doc
Summary: API Documentation for %{name}
Group: Documentation
%if 0%{?fedora} > 9 || 0%{?rhel} >= 6
BuildArch: noarch
%endif

%description doc
This is API documentation generated from the TagLib source code.
%endif


%package devel
Summary: Development files for %{name} 
Group:	 Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig
%if ! %{with doc}
Obsoletes: %{name}-doc
%endif

%description devel
Files needed when building software with %{name}.


%prep
%setup -q -n taglib-%{version}%{?beta}

# patch1 not applied
## omit for now
%patch2 -p1 -b .multilib


%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake} %{?buildtests} -DWITH_ASF=1 -DWITH_MP4=1 ..
popd

make %{?_smp_mflags} -C %{_target_platform}

%if %{with doc}
cd doc
doxygen taglib.doxygen
cd -
%endif


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} -C %{_target_platform}

rm -fr examples/.deps
rm -fr examples/Makefile* examples/CMake*
rm -f %{buildroot}%{_libdir}/lib*.la

%if %{with doc}
rm -fr %{apidocdir} ; mkdir %{apidocdir}
cp -a doc/html doc/*.png %{apidocdir}
ln -s html/index.html %{apidocdir}
find %{apidocdir} -name '*.md5' | xargs rm
%endif


%if %{with tests}
%check
cp -a tests/data %{_target_platform}/tests
cd %{_target_platform}
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH make check
%endif


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING.LGPL NEWS
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%doc examples
%{_bindir}/*-config
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc

%if %{with doc}
%files doc
%defattr(-,root,root,-)
%doc %{apidocdir}/*
%endif


%changelog
* Fri Nov 13 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.6.1-1.1
- Fix conditional for RHEL

* Sat Oct 31 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.6.1-1
- Update to 1.6.1 (bug-fixes, of which one is considered a fix for
  a serious bug: saving of Ogg FLAC comments).

* Thu Sep 17 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.6-2
- Include the new NEWS file as %%doc.

* Mon Sep 14 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.6-1
- Add patch to fix MP4 test on ppc/ppc64.
- Update to 1.6 final.

* Sun Sep  6 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.6-0.1.rc1
- Update to 1.6rc1 (further bug-fixes and support for AIFF and WAV).
- Build optional support for MP4 and ASF/WMA files.

* Fri Sep  4 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.5-8
- Merge another bug-fix from 1.6rc1 (this adds 3 symbols) and
  really add tstring bug-fix:
  * Split Ogg packets larger than 64k into multiple pages. (BUG:171957)
  * Fixed a possible crash in the non-const version of String::operator[]
    and in String::operator+=. (BUG:169389)

* Sun Aug 23 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.5-7
- Build API documentation into -doc package.

* Sat Aug 22 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.5-6
- Add %%check section and conditionally build with tests.
- Update descriptions (and mention the additional file formats).
- Cherry-pick bug-fix patches from 1.6 development (also replaces the
  old taglib-1.5-kde#161721.patch):
  * Fixed crash when saving a Locator APEv2 tag. (BUG:169810)
  * TagLib can now use FLAC padding block. (BUG:107659)
  * Fixed overflow while calculating bitrate of FLAC files with a very
    high bitrate.
  * XiphComment::year() now falls back to YEAR if DATE doesn't exist
    and XiphComment::year() falls back to TRACKNUM if TRACKNUMBER doesn't
    exist. (BUG:144396)
  * Fixed a bug in ByteVectorList::split().
  * Fixed a possible crash in the non-const version of String::operator[]
    and in String::operator+=. (BUG:169389)
  * ID3v2.2 frames are now not incorrectly saved. (BUG:176373)
  * Support for ID3v2.2 PIC frames. (BUG:167786)
  * Improved ID3v2.3 genre parsing. (BUG:188578)
  * Better checking of corrupted ID3v2 APIC data. (BUG:168382)
  * Bitrate calculating using the Xing header now uses floating point
    numbers. (BUG:172556)
  * Added support for PRIV ID3v2 frames.
  * Empty ID3v2 genres are no longer treated as numeric ID3v1 genres.
  * Added support for the POPM (rating/playcount) ID3v2 frame.
  * Fixed crash on handling unsupported ID3v2 frames, e.g. on encrypted
    frames. (BUG:161721)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Dec 12 2008 Rex Dieter <rdieter@fedoraproject.org> 1.5-3
- rebuild for pkgconfig deps

* Mon Oct 06 2008 Rex Dieter <rdieter@fedoraproject.org> 1.5-2
- Encrypted frames taglib/Amarok crash (kde#161721)

* Wed Feb 20 2008 Rex Dieter <rdieter@fedoraproject.org> 1.5-1
- taglib-1.5

* Wed Feb 13 2008 Rex Dieter <rdieter@fedoraproject.org> 1.5-0.9.rc1
- taglib-1.5rc1
- omit taglib-1.4_wchar.diff (for now)

* Mon Feb 04 2008 Rex Dieter <rdieter@fedoraproject.org> 1.5-0.8.b1
- taglib-1.5b1

* Wed Jan 16 2008 Rex Dieter <rdieter[AT]fedoraproject.org> 1.5-0.7.20080116svn
- svn20080116 snapshot
- multiarch conflicts (#343241)

* Sun Nov 11 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 1.5-0.6.20071111svn
- svn20071111 snapshot (#376241)

* Thu Sep 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 1.5-0.5.20070924svn
- -BR: automake 
- +BR: zlib-devel

* Thu Sep 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 1.5-0.4.20070924svn
- use cmake, fixes "taglib_export.h not included" (#272361#c7)

* Mon Sep 24 2007 Aurelien Bompard <abompard@fedoraproject.org> 1.5-0.3.20070924svn
- rebuild

* Mon Sep 24 2007 Aurelien Bompard <abompard@fedoraproject.org> 1.5-0.2.20070924svn
- BR: automake

* Mon Sep 24 2007 Aurelien Bompard <abompard@fedoraproject.org> 1.5-0.1.20070924svn
- update to svn version

* Sun Aug 26 2007 Aurelien Bompard <abompard@fedoraproject.org> 1.4-6
- fix license tag
- rebuild for BuildID

* Thu Dec 14 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.4-5
- add patch for multi-language support

* Thu Sep 14 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.4-4
- have the devel package require pkgconfig (#206443)

* Thu Aug 31 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.4-3
- rebuild

* Tue Feb 21 2006 Aurelien Bompard <gauret[AT]free.fr> 1.4-2
- rebuild for FC5

* Mon Aug 01 2005 Aurelien Bompard <gauret[AT]free.fr> 1.4-1
- version 1.4

* Fri Mar 25 2005 Michael Schwendt <mschwendt[AT]users.sf.net> 1.3.1-2
- rebuild with g++4

* Mon Jan 10 2005 Aurelien Bompard <gauret[AT]free.fr> 0:1.3.1-1
- version 1.3.1
- drop patch0
- don't nuke every .la files, only the useless ones
- spec improvements thanks to Rex Dieter

* Thu Nov 04 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.3-0.fdr.2
- add apeitem.h to the include files in -devel

* Mon Oct 04 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.3-0.fdr.1
- version 1.3

* Sun Jun 06 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.1-0.fdr.5
- Changed license to LGPL
- include examples only in -devel
- remove Makefile* from examples
- remove *.la files

* Fri Jun 04 2004 Mihai Maties <mihai[AT]xcyb.org> 0:1.1-0.fdr.4
- included .la files as well
- compiled doc and included in -devel
- included examples in -devel

* Thu Jun 03 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.1-0.fdr.3
- provide the libtool files in the -devel subpackage
- include exemples in doc

* Thu Jun 03 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.1-0.fdr.2
- remove empty README
- add Requires(post,postun): /sbin/ldconfig
- remove --disable-static, it was useless anyway

* Tue Jun 01 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.1-0.fdr.1
- Fedora submission (shamelessly borrowed from Rex -- kde-redhat.sf.net)

* Sun Apr 04 2004 Rex Dieter <rexdieter at sf.net> 0:1.1-0.fdr.1
- 1.1

* Thu Feb 12 2004 Rex Dieter <rexdieter at sf.net> 0:1.0-0.fdr.1
- fix for rh73

* Fri Feb 06 2004 Rex Dieter <rexdieter at sf.net> 0:1.0-0.fdr.0
- first try
