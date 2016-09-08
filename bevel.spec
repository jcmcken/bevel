%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           bevel 
Version:        0.3.0
Release:        1%{?dist}
Summary:        A simple, shell script subcommand framework

Group:          Utilities
License:        BSD
URL:            https://github.com/jcmcken/bevel
Source0:        %{name}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python
Requires:       python >= 2.6
Requires:       python2

%description
A simple, shell script subcommand framework.

bevel converts a directory structure into a subcommand hierarchy, making the
generation of arbitrary, nested "porcelain" commands very simple.

%prep
%setup -q

%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README.md LICENSE CHANGES.md
%attr(0755,root,root) %{_bindir}/bevel
%{python_sitelib}/*

%changelog
* Thu Sep 08 2016 Jon McKenzie <jcmcken@gmail.com>
Bump to release 0.3.0
* Wed Feb 12 2014 Jon McKenzie <jcmcken@gmail.com>
Bump to release 0.2.0
* Sun Feb 09 2014 Jon McKenzie <jcmcken@gmail.com>
Initial release
