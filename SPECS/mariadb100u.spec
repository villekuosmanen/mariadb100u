# Name of the package without any prefixes
%global pkg_name     mariadb
%global pkgnamepatch mariadb

# Regression tests may take a long time (many cores recommended), skip them by
# passing --nocheck to rpmbuild or by setting runselftest to 0 if defining
# --nocheck is not possible (e.g. in koji build)
%{!?runselftest:%global runselftest 1}

# Set this to 1 to see which tests fail, but 0 on production ready build
%global ignore_testsuite_result 0

# In f20+ use unversioned docdirs, otherwise the old versioned one
%if 0%{?rhel} && 0%{?rhel} <= 7
%global _pkgdocdirname %{name}-%{version}
%else
%global _pkgdocdirname %{name}
%endif

# Use Full RELRO for all binaries (RHBZ#1092548)
%global _hardened_build 1

# By default, patch(1) creates backup files when chunks apply with offsets.
# Turn that off to ensure such files don't get included in RPMs (cf bz#884755).
%global _default_patch_flags --no-backup-if-mismatch

# TokuDB engine is now part of MariaDB, but it is available only for x86_64;
# variable tokudb allows to build with TokuDB storage engine
%bcond_with tokudb

# The Open Query GRAPH engine (OQGRAPH) is a computation engine allowing
# hierarchies and more complex graph structures to be handled in a relational
# fashion; enabled by default
%bcond_without oqgraph

# For some use cases we do not need some parts of the package
%bcond_without clibrary
%bcond_without embedded
%bcond_without devel
%bcond_without client
%bcond_without common
%bcond_without errmsg
%bcond_without bench
%bcond_without test

# When there is already another package that ships /etc/my.cnf,
# rather include it than ship the file again, since conflicts between
# those files may create issues
%bcond_without config

# Include files for SysV init or systemd
%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%bcond_without init_systemd
%bcond_with init_sysv
%global daemon_name mariadb
%global mysqld_unit mysqld
%else
%bcond_with init_systemd
%bcond_without init_sysv
%global daemon_name mysqld
%endif

# MariaDB 10.0 and later requires pcre >= 8.35, otherwise we need to use
# the bundled library, since the package cannot be build with older version
%if 0%{?fedora} >= 21
%bcond_without pcre
%else
%bcond_with pcre
%endif

# We define some system's well known locations here so we can use them easily
# later when building to another location (like SCL)
%global logrotateddir %{_sysconfdir}/logrotate.d
%global logfiledir %{_localstatedir}/log/%{daemon_name}
%global logfile %{logfiledir}/%{daemon_name}.log
%global old_logfile %{_localstatedir}/log/mysqld.log

# Home directory of mysql user should be same for all packages that create it
%global mysqluserhome /var/lib/mysql

# When replacing mysql by mariadb these packages are not upated, but rather
# installed and uninstalled. Thus we loose information about mysqld service
# enablement. To address this we use a file to store that information within
# the transaction. Basically the file is created when mysqld is enabled in
# the beginning of the transaction and mysqld is enabled again in the end
# of the transaction in case this flag file exists.
%global mysqld_enabled_flag_file %{_localstatedir}/lib/rpm-state/mysqld_enabled
%global mysqld_running_flag_file %{_localstatedir}/lib/rpm-state/mysqld_running

# Make long macros shorter
%global sameevr   %{epoch}:%{version}-%{release}
%global compatver 10.0
%global bugfixver 34

Name:             mariadb100u
Version:          %{compatver}.%{bugfixver}
Release:          1.ius%{?dist}
Epoch:            1

Summary:          A community developed branch of MySQL
Group:            Applications/Databases
URL:              http://mariadb.org
# Exceptions allow client libraries to be linked with most open source SW,
# not only GPL code.  See README.mysql-license
License:          GPLv2 with exceptions and LGPLv2 and BSD

Source0:          http://ftp.utexas.edu/mariadb/mariadb-%{version}/source/mariadb-%{version}.tar.gz
Source2:          mysql_config_multilib.sh
Source3:          my.cnf.in
Source5:          README.mysql-cnf
Source6:          README.mysql-docs
Source7:          README.mysql-license
Source10:         mysql.tmpfiles.d.in
Source11:         mysql.service.in
Source12:         mysql-prepare-db-dir.sh
Source13:         mysql-wait-ready.sh
Source14:         mysql-check-socket.sh
Source15:         mysql-scripts-common.sh
Source16:         mysql-compat.service.in
Source17:         mysql-compat.conf.in
Source18:         mysql.init.in
Source50:         rh-skipped-tests-base.list
Source51:         rh-skipped-tests-arm.list
Source52:         rh-skipped-tests-ppc-s390.list
Source60:         rh-skipped-tests-el7.list

# Comments for these patches are in the patch files
# Patches common for more mysql-like packages
Patch1:           %{pkgnamepatch}-strmov.patch
Patch3:           %{pkgnamepatch}-s390-tsc.patch
Patch4:           %{pkgnamepatch}-logrotate.patch
Patch5:           %{pkgnamepatch}-file-contents.patch
Patch7:           %{pkgnamepatch}-scripts.patch
Patch8:           %{pkgnamepatch}-install-db-sharedir.patch

# Patches specific for this mysql package
Patch30:          %{pkgnamepatch}-errno.patch
Patch32:          %{pkgnamepatch}-basedir.patch
Patch35:          %{pkgnamepatch}-config.patch
Patch37:          %{pkgnamepatch}-notestdb.patch

BuildRequires:    cmake
BuildRequires:    libaio-devel
BuildRequires:    readline-devel
BuildRequires:    ncurses-devel
BuildRequires:    systemtap-sdt-devel
BuildRequires:    zlib-devel
BuildRequires:    multilib-rpm-config
BuildRequires:    krb5-devel
BuildRequires:    selinux-policy-devel
%{?with_init_systemd:BuildRequires: systemd systemd-devel}
# auth_pam.so plugin will be build if pam-devel is installed
BuildRequires:    pam-devel
%{?with_pcre:BuildRequires: pcre-devel >= 8.35}
# Few utilities needs Perl
BuildRequires:    perl
# Tests requires time and ps and some perl modules
BuildRequires:    procps
BuildRequires:    time
BuildRequires:    perl(Env)
BuildRequires:    perl(Exporter)
BuildRequires:    perl(Fcntl)
BuildRequires:    perl(File::Temp)
BuildRequires:    perl(Data::Dumper)
BuildRequires:    perl(Getopt::Long)
BuildRequires:    perl(IPC::Open3)
BuildRequires:    perl(Memoize)
BuildRequires:    perl(Socket)
BuildRequires:    perl(Sys::Hostname)
BuildRequires:    perl(Test::More)
BuildRequires:    perl(Time::HiRes)
BuildRequires:    perl(Symbol)
# for running some openssl tests rhbz#1189180
BuildRequires:    openssl openssl-devel

Requires:         bash coreutils grep
Requires:         %{name}-common%{?_isa} = %{sameevr}
# Explicit EVR requirement for -libs is needed for RHBZ#1406320
Requires:         %{name}-libs%{?_isa} = %{sameevr}

# other package names
Conflicts:        MariaDB-client
Conflicts:        mysql-community-client

# IUS things
Provides:         mysql = %{sameevr}
Provides:         mysql%{?_isa} = %{sameevr}
Provides:         mariadb = %{sameevr}
Provides:         mariadb%{?_isa} = %{sameevr}
Conflicts:        mariadb < %{sameevr}

# Filtering: https://fedoraproject.org/wiki/Packaging:AutoProvidesAndRequiresFiltering
%if 0%{?fedora} > 14 || 0%{?rhel} > 6
%global __requires_exclude ^perl\\((hostnames|lib::mtr|lib::v1|mtr_|My::)
%global __provides_exclude_from ^(%{_datadir}/(mysql|mysql-test)/.*|%{_libdir}/mysql/plugin/.*\\.so)$
%else
%filter_from_requires /perl(\(hostnames\|lib::mtr\|lib::v1\|mtr_\|My::\)/d
%filter_provides_in -P (%{_datadir}/(mysql|mysql-test)/.*|%{_libdir}/mysql/plugin/.*\.so)
%filter_setup
%endif


%description
MariaDB is a community developed branch of MySQL.
MariaDB is a multi-user, multi-threaded SQL database server.
It is a client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. The base package
contains the standard MariaDB/MySQL client programs and generic MySQL files.


%if %{with clibrary}
%package          libs
Summary:          The shared libraries required for MariaDB/MySQL clients
Group:            Applications/Databases
Requires:         %{name}-common%{?_isa} = %{sameevr}

# other package names
Conflicts:        MariaDB-shared
Conflicts:        MariaDB-compat
Conflicts:        mysql-community-libs
Conflicts:        mysql-community-libs-compat

# IUS things
Provides:         mysql-libs = %{sameevr}
Provides:         mysql-libs%{?_isa} = %{sameevr}
Provides:         mariadb-libs = %{sameevr}
Provides:         mariadb-libs%{?_isa} = %{sameevr}
Conflicts:        mariadb-libs < %{sameevr}


%description      libs
The mariadb-libs package provides the essential shared libraries for any
MariaDB/MySQL client program or interface. You will need to install this
package to use any other MariaDB package or any clients that need to connect
to a MariaDB/MySQL server. MariaDB is a community developed branch of MySQL.
%endif


%if %{with config}
%package          config
Summary:          The config files required by server and client
Group:            Applications/Databases

# other package names
Conflicts:        MariaDB-common
Conflicts:        mysql-community-server

# IUS things
Provides:         mariadb-config = %{sameevr}
Provides:         mariadb-config%{?_isa} = %{sameevr}
Conflicts:        mariadb-config < %{sameevr}
Conflicts:        mariadb-libs < %{sameevr}


%description      config
The package provides the config file my.cnf and my.cnf.d directory used by any
MariaDB or MySQL program. You will need to install this package to use any
other MariaDB or MySQL package if the config files are not provided in the
package itself.
%endif


%if %{with common}
%package          common
Summary:          The shared files required by server and client
Group:            Applications/Databases
%if %{with config}
Requires:         %{name}-config%{?_isa} = %{sameevr}
%else
Requires:         %{_sysconfdir}/my.cnf
Requires:         %{_sysconfdir}/my.cnf.d
%endif

# other package names
Conflicts:        MariaDB-common
Conflicts:        mysql-community-common

# IUS things
Provides:         mariadb-common = %{sameevr}
Provides:         mariadb-common%{?_isa} = %{sameevr}
Conflicts:        mariadb-common < %{sameevr}
Conflicts:        mariadb-libs < %{sameevr}


%description      common
The package provides the essential shared files for any MariaDB program.
You will need to install this package to use any other MariaDB package.
%endif


%if %{with errmsg}
%package          errmsg
Summary:          The error messages files required by server and embedded
Group:            Applications/Databases
Requires:         %{name}-common%{?_isa} = %{sameevr}

# other package names
Conflicts:        MariaDB-server
Conflicts:        mysql-community-common

# IUS things
Provides:         mariadb-errmsg = %{sameevr}
Provides:         mariadb-errmsg%{?_isa} = %{sameevr}
Conflicts:        mariadb-errmsg < %{sameevr}
Conflicts:        mariadb-libs < %{sameevr}


%description      errmsg
The package provides error messages files for the MariaDB daemon and the
embedded server. You will need to install this package to use any of those
MariaDB packages.
%endif


%package          server
Summary:          The MariaDB server and related files
Group:            Applications/Databases

# note: no version here = %%{version}-%%{release}
Requires:         %{name}%{?_isa}
Requires:         %{name}-libs%{?_isa} = %{sameevr}
Requires:         %{name}-common%{?_isa} = %{sameevr}
%if %{with config}
Requires:         %{name}-config%{?_isa} = %{sameevr}
%else
Requires:         %{_sysconfdir}/my.cnf
Requires:         %{_sysconfdir}/my.cnf.d
%endif
Requires:         %{name}-errmsg%{?_isa} = %{sameevr}
Requires:         sh-utils
Requires(pre):    /usr/sbin/useradd
%if %{with init_systemd}
# We require this to be present for %%{_tmpfilesdir}
Requires:         systemd
# Make sure it's there when scriptlets run, too
Requires(pre):    systemd
Requires(posttrans): systemd
%{?systemd_requires: %systemd_requires}
%endif
# mysqlhotcopy needs DBI/DBD support
Requires:         perl(DBI)
Requires:         perl(DBD::mysql)

# other package names
Conflicts:        MariaDB-server
Conflicts:        mysql-community-server

# IUS things
Provides:         mysql-compat-server = %{sameevr}
Provides:         mysql-compat-server%{?_isa} = %{sameevr}
Provides:         mariadb-server = %{sameevr}
Provides:         mariadb-server%{?_isa} = %{sameevr}
Conflicts:        mariadb-server < %{sameevr}


%description      server
MariaDB is a multi-user, multi-threaded SQL database server. It is a
client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. This package contains
the MariaDB server and some accompanying files and directories.
MariaDB is a community developed branch of MySQL.


%if %{with oqgraph}
%package          oqgraph
Summary:          The Open Query GRAPH engine for MariaDB
Group:            Applications/Databases
Requires:         %{name}-server%{?_isa} = %{sameevr}
# boost and Judy required for oograph
BuildRequires:    boost-devel
BuildRequires:    Judy-devel

# other package names
Conflicts:        MariaDB-oqgraph-engine

# IUS things
Provides:         mariadb-oqgraph = %{sameevr}
Provides:         mariadb-oqgraph%{?_isa} = %{sameevr}
Conflicts:        mariadb-oqgraph < %{sameevr}


%description      oqgraph
The package provides Open Query GRAPH engine (OQGRAPH) as plugin for MariaDB
database server. OQGRAPH is a computation engine allowing hierarchies and more
complex graph structures to be handled in a relational fashion. In a nutshell,
tree structures and friend-of-a-friend style searches can now be done using
standard SQL syntax, and results joined onto other tables.
%endif


%if %{with devel}
%package          devel
Summary:          Files for development of MariaDB/MySQL applications
Group:            Applications/Databases
Requires:         %{name}-libs%{?_isa} = %{sameevr}
Requires:         openssl-devel%{?_isa}

# other package names
Conflicts:        MariaDB-devel
Conflicts:        mysql-community-devel

# IUS things
Provides:         mysql-devel = %{sameevr}
Provides:         mysql-devel%{?_isa} = %{sameevr}
Provides:         mariadb-devel = %{sameevr}
Provides:         mariadb-devel%{?_isa} = %{sameevr}
Conflicts:        mariadb-devel < %{sameevr}


%description      devel
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains the libraries and header files that are needed for
developing MariaDB/MySQL client applications.
MariaDB is a community developed branch of MySQL.
%endif


%if %{with embedded}
%package          embedded
Summary:          MariaDB as an embeddable library
Group:            Applications/Databases
Requires:         %{name}-common%{?_isa} = %{sameevr}
Requires:         %{name}-errmsg%{?_isa} = %{sameevr}

# other package names
Conflicts:        MariaDB-server
Conflicts:        mysql-community-embedded
Conflicts:        mysql-community-embedded-compat

# IUS things
Provides:         mariadb-embedded = %{sameevr}
Provides:         mariadb-embedded%{?_isa} = %{sameevr}
Conflicts:        mariadb-embedded < %{sameevr}


%description      embedded
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains a version of the MariaDB server that can be embedded
into a client application instead of running as a separate process.
MariaDB is a community developed branch of MySQL.


%package          embedded-devel
Summary:          Development files for MariaDB as an embeddable library
Group:            Applications/Databases
Requires:         %{name}-embedded%{?_isa} = %{sameevr}
Requires:         %{name}-devel%{?_isa} = %{sameevr}
# embedded-devel should require libaio-devel (rhbz#1290517)
Requires:         libaio-devel

# other package names
Conflicts:        mysql-community-embedded-devel

# IUS things
Provides:         mariadb-embedded-devel = %{sameevr}
Provides:         mariadb-embedded-devel%{?_isa} = %{sameevr}
Conflicts:        mariadb-embedded-devel < %{sameevr}


%description      embedded-devel
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains files needed for developing and testing with
the embedded version of the MariaDB server.
MariaDB is a community developed branch of MySQL.
%endif


%if %{with bench}
%package          bench
Summary:          MariaDB benchmark scripts and data
Group:            Applications/Databases
Requires:         %{name}%{?_isa} = %{sameevr}

# other package names
Conflicts:        mysql-community-bench

# IUS things
Provides:         mariadb-bench = %{sameevr}
Provides:         mariadb-bench%{?_isa} = %{sameevr}
Conflicts:        mariadb-bench < %{sameevr}


%description      bench
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains benchmark scripts and data for use when benchmarking
MariaDB.
MariaDB is a community developed branch of MySQL.
%endif


%if %{with test}
%package          test
Summary:          The test suite distributed with MariaDB
Group:            Applications/Databases
Requires:         %{name}%{?_isa} = %{sameevr}
Requires:         %{name}-common%{?_isa} = %{sameevr}
Requires:         %{name}-server%{?_isa} = %{sameevr}
Requires:         perl(Env)
Requires:         perl(Exporter)
Requires:         perl(Fcntl)
Requires:         perl(File::Temp)
Requires:         perl(Data::Dumper)
Requires:         perl(Getopt::Long)
Requires:         perl(IPC::Open3)
Requires:         perl(Socket)
Requires:         perl(Sys::Hostname)
Requires:         perl(Test::More)
Requires:         perl(Time::HiRes)

# other package names
Conflicts:        MariaDB-test
Conflicts:        mysql-community-test

# IUS things
Provides:         mariadb-test = %{sameevr}
Provides:         mariadb-test%{?_isa} = %{sameevr}
Conflicts:        mariadb-test < %{sameevr}


%description      test
MariaDB is a multi-user, multi-threaded SQL database server. This
package contains the regression test suite distributed with
the MariaDB sources.
MariaDB is a community developed branch of MySQL.
%endif


%prep
%setup -q -n mariadb-%{version}

%patch1 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch7 -p1
%patch8 -p1
%patch30 -p1
%patch32 -p1
%patch35 -p1
%patch37 -p1

sed -i -e 's/2.8.7/2.6.4/g' cmake/cpack_rpm.cmake

# workaround for upstream bug #56342
rm -f mysql-test/t/ssl_8k_key-master.opt

# generate a list of tests that fail, but are not disabled by upstream
cat %{SOURCE50} | tee mysql-test/rh-skipped-tests.list

# disable some tests failing on different architectures
%ifarch %{arm} aarch64
cat %{SOURCE51} | tee -a mysql-test/rh-skipped-tests.list
%endif

%ifarch ppc ppc64 ppc64p7 s390 s390x
cat %{SOURCE52} | tee -a mysql-test/rh-skipped-tests.list
%endif

%if 0%{?rhel} && 0%{?rhel} <= 7
cat %{SOURCE60} | tee -a mysql-test/rh-skipped-tests.list
%endif

cp %{SOURCE2} %{SOURCE3} %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13} \
   %{SOURCE14} %{SOURCE15} %{SOURCE16} %{SOURCE17} %{SOURCE18} scripts


%build

# fail quickly and obviously if user tries to build as root
%if %runselftest
    if [ x"$(id -u)" = "x0" ]; then
        echo "mysql's regression tests fail if run as root."
        echo "If you really need to build the RPM as root, use"
        echo "--nocheck to skip the regression tests."
        exit 1
    fi
%endif

CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE"
# force PIC mode so that we can build libmysqld.so
CFLAGS="$CFLAGS -fPIC"
# GCC 4.9 causes segfaults: https://mariadb.atlassian.net/browse/MDEV-6360
CFLAGS="$CFLAGS -fno-delete-null-pointer-checks"
# gcc seems to have some bugs on sparc as of 4.4.1, back off optimization
# submitted as bz #529298
%ifarch sparc sparcv9 sparc64
CFLAGS=`echo $CFLAGS| sed -e "s|-O2|-O1|g" `
%endif
# significant performance gains can be achieved by compiling with -O3 optimization
# rhbz#1051069
%ifarch ppc64
CFLAGS=`echo $CFLAGS| sed -e "s|-O2|-O3|g" `
%endif
CXXFLAGS="$CFLAGS"
export CFLAGS CXXFLAGS

%if 0%{?_hardened_build}
# building with PIE
LDFLAGS="$LDFLAGS -pie -Wl,-z,relro,-z,now"
export LDFLAGS
%endif

# The INSTALL_xxx macros have to be specified relative to CMAKE_INSTALL_PREFIX
# so we can't use %%{_datadir} and so forth here.
cmake .  -DBUILD_CONFIG=mysql_release \
         -DFEATURE_SET="community" \
         -DINSTALL_LAYOUT=RPM \
         -DDAEMON_NAME="%{daemon_name}" \
%if 0%{?mysqld_unit:1}
         -DDAEMON_NAME_COMPAT="%{mysqld_unit}" \
%endif
         -DLOG_LOCATION="%{logfile}" \
         -DLOG_LOCATION_COMPAT="%{old_logfile}" \
         -DPID_FILE_DIR="%{_localstatedir}/run/%{daemon_name}" \
         -DPID_FILE_DIR_COMPAT="%{_localstatedir}/run/%{mysqld_unit}" \
         -DNICE_PROJECT_NAME="MariaDB" \
         -DRPM="%{?rhel:rhel%{rhel}}%{!?rhel:fedora%{fedora}}" \
         -DCMAKE_INSTALL_PREFIX="%{_prefix}" \
         -DINSTALL_SYSCONFDIR="%{_sysconfdir}" \
         -DINSTALL_SYSCONF2DIR="%{_sysconfdir}/my.cnf.d" \
         -DINSTALL_DOCDIR="share/doc/%{_pkgdocdirname}" \
         -DINSTALL_DOCREADMEDIR="share/doc/%{_pkgdocdirname}" \
         -DINSTALL_INCLUDEDIR=include/mysql \
         -DINSTALL_INFODIR=share/info \
         -DINSTALL_LIBDIR="%{_lib}/mysql" \
         -DINSTALL_MANDIR=share/man \
         -DINSTALL_MYSQLSHAREDIR=share/%{pkg_name} \
         -DINSTALL_MYSQLTESTDIR=share/mysql-test \
         -DINSTALL_PLUGINDIR="%{_lib}/mysql/plugin" \
         -DINSTALL_SBINDIR=libexec \
         -DINSTALL_SCRIPTDIR=bin \
         -DINSTALL_SQLBENCHDIR=share \
         -DINSTALL_SUPPORTFILESDIR=share/%{pkg_name} \
         -DMYSQL_DATADIR="%{_localstatedir}/lib/mysql" \
         -DMYSQL_UNIX_ADDR="%{_localstatedir}/lib/mysql/mysql.sock" \
         -DENABLED_LOCAL_INFILE=ON \
         -DENABLE_DTRACE=ON \
         -DWITH_EMBEDDED_SERVER=ON \
         -DWITH_READLINE=ON \
         -DWITH_SSL=system \
         -DWITH_ZLIB=system \
%{?with_pcre: -DWITH_PCRE=system}\
         -DWITH_JEMALLOC=no \
%{!?with_tokudb: -DWITHOUT_TOKUDB=ON}\
%{!?with_oqgraph: -DWITHOUT_OQGRAPH=ON}\
         -DTMPDIR=/var/tmp \
         %{?_hardened_build:-DWITH_MYSQLD_LDFLAGS="-pie -Wl,-z,relro,-z,now"}

make %{?_smp_mflags} VERBOSE=1

# debuginfo extraction scripts fail to find source files in their real
# location -- satisfy them by copying these files into location, which
# is expected by scripts
for e in innobase xtradb ; do
  for f in pars0grm.y pars0lex.l ; do
    cp -p "storage/$e/pars/$f" "storage/$e/$f"
  done
done


%install
make DESTDIR=%{buildroot} install

# cmake generates some completely wacko references to -lprobes_mysql when
# building with dtrace support.  Haven't found where to shut that off,
# so resort to this blunt instrument.  While at it, let's not reference
# libmysqlclient_r anymore either.
sed -e 's/-lprobes_mysql//' -e 's/-lmysqlclient_r/-lmysqlclient/' \
  %{buildroot}%{_bindir}/mysql_config >mysql_config.tmp
cp -p -f mysql_config.tmp %{buildroot}%{_bindir}/mysql_config
chmod 755 %{buildroot}%{_bindir}/mysql_config

# multilib header support
for header in mysql/my_config.h mysql/private/config.h; do
%multilib_fix_c_header --file %{_includedir}/$header
done

# multilib support for shell scripts
# we only apply this to known Red Hat multilib arches, per bug #181335
if %multilib_capable; then
mv %{buildroot}%{_bindir}/mysql_config %{buildroot}%{_bindir}/mysql_config-%{__isa_bits}
install -p -m 0755 scripts/mysql_config_multilib %{buildroot}%{_bindir}/mysql_config
fi

# install INFO_SRC, INFO_BIN into libdir (upstream thinks these are doc files,
# but that's pretty wacko --- see also %%{name}-file-contents.patch)
install -p -m 644 Docs/INFO_SRC %{buildroot}%{_libdir}/mysql/
install -p -m 644 Docs/INFO_BIN %{buildroot}%{_libdir}/mysql/
rm -r %{buildroot}%{_pkgdocdir}/MariaDB-server-%{version}/

mkdir -p %{buildroot}%{logfiledir}
chmod 0750 %{buildroot}%{logfiledir}
touch %{buildroot}%{logfile}
%if 0%{?old_logfile:1}
ln -s %{logfile} %{buildroot}%{old_logfile}
%endif

# current setting in my.cnf is to use /var/run/mariadb for creating pid file,
# however since my.cnf is not updated by RPM if changed, we need to create mysqld
# as well because users can have odd settings in their /etc/my.cnf
%{?mysqld_unit:mkdir -p %{buildroot}%{_localstatedir}/run/%{mysqld_unit}}
mkdir -p %{buildroot}%{_localstatedir}/run/%{daemon_name}
install -p -m 0755 -d %{buildroot}%{_localstatedir}/lib/mysql

%if %{with config}
install -D -p -m 0644 scripts/my.cnf %{buildroot}%{_sysconfdir}/my.cnf
%else
rm -f %{buildroot}%{_sysconfdir}/my.cnf.d/mysql-clients.cnf
rm -f %{buildroot}%{_sysconfdir}/my.cnf
%endif

# install systemd unit files and scripts for handling server startup
%if %{with init_systemd}
install -D -p -m 644 scripts/mysql.service %{buildroot}%{_unitdir}/%{daemon_name}.service
install -D -p -m 0644 scripts/mysql.tmpfiles.d %{buildroot}%{_tmpfilesdir}/%{daemon_name}.conf
%endif

# install alternative systemd unit file for compatibility reasons
%if 0%{?mysqld_unit:1}
install -p -m 644 scripts/mysql-compat.service %{buildroot}%{_unitdir}/%{mysqld_unit}.service
mkdir -p %{buildroot}%{_unitdir}/%{daemon_name}.service.d
install -p -m 644 scripts/mysql-compat.conf %{buildroot}%{_unitdir}/%{daemon_name}.service.d/mysql-compat.conf
%endif

# install SysV init script
%if %{with init_sysv}
install -D -p -m 755 scripts/mysql.init %{buildroot}%{_initddir}/%{daemon_name}
%endif

# helper scripts for service starting
install -p -m 755 scripts/mysql-prepare-db-dir %{buildroot}%{_libexecdir}/mysql-prepare-db-dir
install -p -m 755 scripts/mysql-wait-ready %{buildroot}%{_libexecdir}/mysql-wait-ready
install -p -m 755 scripts/mysql-check-socket %{buildroot}%{_libexecdir}/mysql-check-socket
install -p -m 644 scripts/mysql-scripts-common %{buildroot}%{_libexecdir}/mysql-scripts-common

# Remove libmysqld.a
rm -f %{buildroot}%{_libdir}/mysql/libmysqld.a

# libmysqlclient_r is no more.  Upstream tries to replace it with symlinks
# but that really doesn't work (wrong soname in particular).  We'll keep
# just the devel libmysqlclient_r.so link, so that rebuilding without any
# source change is enough to get rid of dependency on libmysqlclient_r.
rm -f %{buildroot}%{_libdir}/mysql/libmysqlclient_r.so*
ln -s libmysqlclient.so %{buildroot}%{_libdir}/mysql/libmysqlclient_r.so

# mysql-test includes one executable that doesn't belong under /usr/share,
# so move it and provide a symlink
mv %{buildroot}%{_datadir}/mysql-test/lib/My/SafeProcess/my_safe_process %{buildroot}%{_bindir}
ln -s ../../../../../bin/my_safe_process %{buildroot}%{_datadir}/mysql-test/lib/My/SafeProcess/my_safe_process

# should move this to /etc/ ?
rm -f %{buildroot}%{_bindir}/mysql_embedded
rm -f %{buildroot}%{_libdir}/mysql/*.a
rm -f %{buildroot}%{_datadir}/%{pkg_name}/binary-configure
rm -f %{buildroot}%{_datadir}/%{pkg_name}/magic
rm -f %{buildroot}%{_datadir}/%{pkg_name}/ndb-config-2-node.ini
rm -f %{buildroot}%{_datadir}/%{pkg_name}/mysql.server
rm -f %{buildroot}%{_datadir}/%{pkg_name}/mysqld_multi.server
rm -f %{buildroot}%{_mandir}/man1/mysql-stress-test.pl.1*
rm -f %{buildroot}%{_mandir}/man1/mysql-test-run.pl.1*
rm -f %{buildroot}%{_bindir}/mytop

# put logrotate script where it needs to be
mkdir -p %{buildroot}%{logrotateddir}
mv %{buildroot}%{_datadir}/%{pkg_name}/mysql-log-rotate %{buildroot}%{logrotateddir}/%{daemon_name}
chmod 644 %{buildroot}%{logrotateddir}/%{daemon_name}

mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/mysql" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{pkg_name}-%{_arch}.conf

# copy additional docs into build tree so %%doc will find them
install -p -m 0644 %{SOURCE5} %{basename:%{SOURCE5}}
install -p -m 0644 %{SOURCE6} %{basename:%{SOURCE6}}
install -p -m 0644 %{SOURCE7} %{basename:%{SOURCE7}}
install -p -m 0644 %{SOURCE16} %{basename:%{SOURCE16}}

# install the list of skipped tests to be available for user runs
install -p -m 0644 mysql-test/rh-skipped-tests.list %{buildroot}%{_datadir}/mysql-test

# remove unneeded RHEL-4 SELinux stuff
rm -rf %{buildroot}%{_datadir}/%{pkg_name}/SELinux/

# remove SysV init script
rm -f %{buildroot}%{_sysconfdir}/init.d/mysql

# remove duplicate logrotate script
rm -f %{buildroot}%{logrotateddir}/mysql

# remove solaris files
rm -rf %{buildroot}%{_datadir}/%{pkg_name}/solaris/

# remove *.jar file from mysql-test
rm -rf %{buildroot}%{_datadir}/mysql-test/plugin/connect/connect/std_data/JdbcMariaDB.jar

%if %{without clibrary}
rm -rf %{buildroot}%{_libdir}/mysql/libmysqlclient*.so.*
rm -rf %{buildroot}%{_sysconfdir}/ld.so.conf.d
%endif

%if %{without embedded}
rm -f %{buildroot}%{_libdir}/mysql/libmysqld.so*
rm -f %{buildroot}%{_bindir}/{mysql_client_test_embedded,mysqltest_embedded}
rm -f %{buildroot}%{_mandir}/man1/{mysql_client_test_embedded,mysqltest_embedded}.1*
%endif

%if %{without devel}
rm -f %{buildroot}%{_bindir}/mysql_config*
rm -rf %{buildroot}%{_includedir}/mysql
rm -f %{buildroot}%{_datadir}/aclocal/mysql.m4
rm -f %{buildroot}%{_libdir}/mysql/libmysqlclient*.so
rm -f %{buildroot}%{_mandir}/man1/mysql_config.1*
%endif

%if %{without client}
rm -f %{buildroot}%{_bindir}/{msql2mysql,mysql,mysql_find_rows,mysql_waitpid,\
mysqlaccess,mysqladmin,mysqlbinlog,mysqlcheck,mysqldump,tokuftdump,tokuft_logprint,mysqlimport,\
mysqlshow,mysqlslap,my_print_defaults,aria_chk,aria_dump_log,aria_ftdump,\
aria_pack,aria_read_log}
rm -f %{buildroot}%{_mandir}/man1/{mysql,mysql_find_rows,mysql_waitpid,\
mysqlaccess,mysqladmin,mysqldump,mysqlshow,mysqlslap,\
my_print_defaults}.1*
rm -f %{buildroot}%{_sysconfdir}/my.cnf.d/{client,connect}.cnf
%endif

%if %{without config}
rm -f %{buildroot}%{_sysconfdir}/my.cnf
rm -f %{buildroot}%{_sysconfdir}/my.cnf.d/mysql-clients.cnf
%endif

%if %{without common}
rm -rf %{buildroot}%{_datadir}/%{pkg_name}/charsets
%endif

%if %{without errmsg}
rm -rf %{buildroot}%{_datadir}/%{pkg_name}/{english,czech,danish,dutch,estonian,\
french,german,greek,hungarian,italian,japanese,korean,norwegian,norwegian-ny,\
polish,portuguese,romanian,russian,serbian,slovak,spanish,swedish,ukrainian}
%endif

%if %{without bench}
rm -rf %{buildroot}%{_datadir}/sql-bench
%endif

%if %{without test}
rm -f %{buildroot}%{_bindir}/{mysql_client_test,my_safe_process}
rm -rf %{buildroot}%{_datadir}/mysql-test
rm -f %{buildroot}%{_mandir}/man1/mysql_client_test.1*
%endif


%check
%if %{with test}
%if %runselftest
make test VERBOSE=1
# hack to let 32- and 64-bit tests run concurrently on same build machine
export MTR_PARALLEL=1
# builds might happen at the same host, avoid collision
export MTR_BUILD_THREAD=%{__isa_bits}

# The cmake build scripts don't provide any simple way to control the
# options for mysql-test-run, so ignore the make target and just call it
# manually.  Nonstandard options chosen are:
# --force to continue tests after a failure
# no retries please
# test SSL with --ssl
# skip tests that are listed in rh-skipped-tests.list
# avoid redundant test runs with --binlog-format=mixed
# increase timeouts to prevent unwanted failures during mass rebuilds
(
  set -e
  cd mysql-test
  perl ./mysql-test-run.pl --force --retry=0 --ssl \
    --suite-timeout=720 --testcase-timeout=30 --skip-rpl \
    --mysqld=--binlog-format=mixed --force-restart \
    --shutdown-timeout=60 --max-test-fail=0 \
%if %{ignore_testsuite_result}
    || :
%else
    --skip-test-list=rh-skipped-tests.list
%endif
  # cmake build scripts will install the var cruft if left alone :-(
  rm -rf var
)
%endif
%endif


%pre server
/usr/sbin/groupadd -g 27 -o -r mysql >/dev/null 2>&1 || :
/usr/sbin/useradd -M -N -g mysql -o -r -d %{mysqluserhome} -s /sbin/nologin \
  -c "MySQL Server" -u 27 mysql >/dev/null 2>&1 || :

%if %{with init_systemd}
# Explicitly enable mysqld if it was enabled in the beginning
# of the transaction. Otherwise mysqld is disabled always when
# replacing mysql with mariadb, because it is not recognized
# as updating, but rather as removal and install.
if /bin/systemctl is-enabled mysqld.service >/dev/null 2>&1 ; then
    touch %mysqld_enabled_flag_file >/dev/null 2>&1 || :
fi

# Since mysqld.service became a symlink to mariadb.service, turning off
# the running mysqld service doesn't work fine (BZ#1002996). As a work-around
# we explicitly stop mysqld before upgrade and start after it again.
if [ ! -L %{_unitdir}/mysqld.service ] && /bin/systemctl is-active mysqld.service &>/dev/null ; then
    touch %mysqld_running_flag_file >/dev/null 2>&1 || :
    /bin/systemctl stop mysqld.service >/dev/null 2>&1 || :
fi

%posttrans server
if [ -f %mysqld_enabled_flag_file ] ; then
    /bin/systemctl enable %{daemon_name}.service >/dev/null 2>&1 || :
    rm -f %mysqld_enabled_flag_file >/dev/null 2>&1 || :
fi
if [ -f %mysqld_running_flag_file ] ; then
    /bin/systemctl start %{daemon_name}.service >/dev/null 2>&1 || :
    rm -f %mysqld_running_flag_file >/dev/null 2>&1 || :
fi
%endif

%if %{with clibrary}
%post libs -p /sbin/ldconfig
%endif


%if %{with embedded}
%post embedded -p /sbin/ldconfig
%endif


%post server
%if %{with init_systemd}
%systemd_post %{daemon_name}.service
%endif
%if %{with init_sysv}
if [ $1 = 1 ]; then
    /sbin/chkconfig --add %{daemon_name}
fi
%endif


%preun server
%if %{with init_systemd}
%systemd_preun %{daemon_name}.service
%endif
%if %{with init_sysv}
if [ $1 = 0 ]; then
    /sbin/service %{daemon_name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{daemon_name}
fi
%endif


%if %{with clibrary}
%postun libs -p /sbin/ldconfig
%endif


%if %{with embedded}
%postun embedded -p /sbin/ldconfig
%endif


%postun server
%if %{with init_systemd}
%systemd_postun_with_restart %{daemon_name}.service
%endif
%if %{with init_sysv}
if [ $1 -ge 1 ]; then
    /sbin/service %{daemon_name} condrestart >/dev/null 2>&1 || :
fi
%endif


%if %{with client}
%files
%{_bindir}/msql2mysql
%{_bindir}/mysql
%{_bindir}/mysql_find_rows
%{_bindir}/mysql_waitpid
%{_bindir}/mysqlaccess
%{_bindir}/mysqladmin
%{_bindir}/mysqlbinlog
%{_bindir}/mysqlcheck
%{_bindir}/mysqldump
%{?with_tokudb:%{_bindir}/tokuftdump}
%{?with_tokudb:%{_bindir}/tokuft_logprint}
%{_bindir}/mysqlimport
%{_bindir}/mysqlshow
%{_bindir}/mysqlslap
%{_bindir}/my_print_defaults
%{_bindir}/aria_chk
%{_bindir}/aria_dump_log
%{_bindir}/aria_ftdump
%{_bindir}/aria_pack
%{_bindir}/aria_read_log

%{_mandir}/man1/mysql.1*
%{_mandir}/man1/mysql_find_rows.1*
%{_mandir}/man1/mysql_waitpid.1*
%{_mandir}/man1/mysqlaccess.1*
%{_mandir}/man1/mysqladmin.1*
%{_mandir}/man1/mysqldump.1*
%{_mandir}/man1/mysqlshow.1*
%{_mandir}/man1/mysqlslap.1*
%{_mandir}/man1/my_print_defaults.1*
%{_mandir}/man1/aria_chk.1*
%{_mandir}/man1/aria_dump_log.1*
%{_mandir}/man1/aria_ftdump.1*
%{_mandir}/man1/aria_pack.1*
%{_mandir}/man1/aria_read_log.1*

%config(noreplace) %{_sysconfdir}/my.cnf.d/client.cnf
%config(noreplace) %{_sysconfdir}/my.cnf.d/connect.cnf
%endif

%if %{with clibrary}
%files libs
%{_libdir}/mysql/libmysqlclient.so.*
%{_sysconfdir}/ld.so.conf.d/*
%endif

%if %{with config}
%files config
# although the default my.cnf contains only server settings, we put it in the
# common package because it can be used for client settings too.
%dir %{_sysconfdir}/my.cnf.d
%config(noreplace) %{_sysconfdir}/my.cnf
%config(noreplace) %{_sysconfdir}/my.cnf.d/mysql-clients.cnf
%endif

%if %{with common}
%files common
%license COPYING storage/innobase/COPYING.Percona storage/innobase/COPYING.Google
%doc README README.mysql-license README.mysql-docs
%dir %{_libdir}/mysql
%dir %{_datadir}/%{pkg_name}
%{_datadir}/%{pkg_name}/charsets
%endif

%if %{with errmsg}
%files errmsg
%{_datadir}/%{pkg_name}/english
%lang(cs) %{_datadir}/%{pkg_name}/czech
%lang(da) %{_datadir}/%{pkg_name}/danish
%lang(nl) %{_datadir}/%{pkg_name}/dutch
%lang(et) %{_datadir}/%{pkg_name}/estonian
%lang(fr) %{_datadir}/%{pkg_name}/french
%lang(de) %{_datadir}/%{pkg_name}/german
%lang(el) %{_datadir}/%{pkg_name}/greek
%lang(hu) %{_datadir}/%{pkg_name}/hungarian
%lang(it) %{_datadir}/%{pkg_name}/italian
%lang(ja) %{_datadir}/%{pkg_name}/japanese
%lang(ko) %{_datadir}/%{pkg_name}/korean
%lang(no) %{_datadir}/%{pkg_name}/norwegian
%lang(no) %{_datadir}/%{pkg_name}/norwegian-ny
%lang(pl) %{_datadir}/%{pkg_name}/polish
%lang(pt) %{_datadir}/%{pkg_name}/portuguese
%lang(ro) %{_datadir}/%{pkg_name}/romanian
%lang(ru) %{_datadir}/%{pkg_name}/russian
%lang(sr) %{_datadir}/%{pkg_name}/serbian
%lang(sk) %{_datadir}/%{pkg_name}/slovak
%lang(es) %{_datadir}/%{pkg_name}/spanish
%lang(sv) %{_datadir}/%{pkg_name}/swedish
%lang(uk) %{_datadir}/%{pkg_name}/ukrainian
%endif


%files server
%doc support-files/*.cnf README.mysql-cnf

%{_bindir}/myisamchk
%{_bindir}/myisam_ftdump
%{_bindir}/myisamlog
%{_bindir}/myisampack
%{_bindir}/mysql_convert_table_format
%{_bindir}/mysql_fix_extensions
%{_bindir}/mysql_install_db
%{_bindir}/mysql_plugin
%{_bindir}/mysql_secure_installation
%{_bindir}/mysql_setpermission
%{_bindir}/mysql_tzinfo_to_sql
%{_bindir}/mysql_upgrade
%{_bindir}/mysql_zap
%{_bindir}/mysqlbug
%{_bindir}/mysqldumpslow
%{_bindir}/mysqld_multi
%{_bindir}/mysqld_safe
%{_bindir}/mysqld_safe_helper
%{_bindir}/mysqlhotcopy
%{_bindir}/mysqltest
%{_bindir}/innochecksum
%{_bindir}/perror
%{_bindir}/replace
%{_bindir}/resolve_stack_dump
%{_bindir}/resolveip

%config(noreplace) %{_sysconfdir}/my.cnf.d/server.cnf
%{?with_tokudb:%config(noreplace) %{_sysconfdir}/my.cnf.d/tokudb.cnf}

%{_libexecdir}/mysqld

%{_libdir}/mysql/INFO_SRC
%{_libdir}/mysql/INFO_BIN
%if %{without common}
%dir %{_datadir}/%{name}
%endif

%{_libdir}/mysql/plugin
%{?with_oqgraph:%exclude %{_libdir}/mysql/plugin/ha_oqgraph.so}

%{_mandir}/man1/msql2mysql.1*
%{_mandir}/man1/myisamchk.1*
%{_mandir}/man1/myisamlog.1*
%{_mandir}/man1/myisampack.1*
%{_mandir}/man1/mysql_convert_table_format.1*
%{_mandir}/man1/myisam_ftdump.1*
%{_mandir}/man1/mysql.server.1*
%{_mandir}/man1/mysql_fix_extensions.1*
%{_mandir}/man1/mysql_install_db.1*
%{_mandir}/man1/mysql_plugin.1*
%{_mandir}/man1/mysql_secure_installation.1*
%{_mandir}/man1/mysql_upgrade.1*
%{_mandir}/man1/mysql_zap.1*
%{_mandir}/man1/mysqlbug.1*
%{_mandir}/man1/mysqldumpslow.1*
%{_mandir}/man1/mysqlbinlog.1*
%{_mandir}/man1/mysqlcheck.1*
%{_mandir}/man1/mysqld_multi.1*
%{_mandir}/man1/mysqld_safe.1*
%{_mandir}/man1/mysqlhotcopy.1*
%{_mandir}/man1/mysqlimport.1*
%{_mandir}/man1/mysql_setpermission.1*
%{_mandir}/man1/mysqltest.1*
%{_mandir}/man1/innochecksum.1*
%{_mandir}/man1/perror.1*
%{_mandir}/man1/replace.1*
%{_mandir}/man1/resolve_stack_dump.1*
%{_mandir}/man1/resolveip.1*
%{_mandir}/man1/mysql_tzinfo_to_sql.1*
%{_mandir}/man8/mysqld.8*

%{_datadir}/%{pkg_name}/errmsg-utf8.txt
%{_datadir}/%{pkg_name}/fill_help_tables.sql
%{_datadir}/%{pkg_name}/install_spider.sql
%{_datadir}/%{pkg_name}/mroonga/install.sql
%{_datadir}/%{pkg_name}/mroonga/uninstall.sql
%{_datadir}/%{pkg_name}/mysql_system_tables.sql
%{_datadir}/%{pkg_name}/mysql_system_tables_data.sql
%{_datadir}/%{pkg_name}/mysql_test_data_timezone.sql
%{_datadir}/%{pkg_name}/mysql_performance_tables.sql
%{_datadir}/%{pkg_name}/my-*.cnf

%{?mysqld_unit:%{_unitdir}/%{mysqld_unit}.service}
%{?mysqld_unit:%{_unitdir}/%{daemon_name}.service.d/mysql-compat.conf}
%{?with_init_systemd:%{_unitdir}/%{daemon_name}.service}
%{?with_init_sysv:%{_initddir}/%{daemon_name}}
%{_libexecdir}/mysql-prepare-db-dir
%{_libexecdir}/mysql-wait-ready
%{_libexecdir}/mysql-check-socket
%{_libexecdir}/mysql-scripts-common

%{?with_init_systemd:%{_tmpfilesdir}/%{daemon_name}.conf}
%{?mysqld_unit:%attr(0755,mysql,mysql) %dir %{_localstatedir}/run/%{mysqld_unit}}
%attr(0755,mysql,mysql) %dir %{_localstatedir}/run/%{daemon_name}
%attr(0755,mysql,mysql) %dir %{_localstatedir}/lib/mysql
%attr(0750,mysql,mysql) %dir %{logfiledir}
%attr(0640,mysql,mysql) %config %ghost %verify(not md5 size mtime) %{logfile}
%if 0%{?old_logfile:1}
                        %config %ghost %verify(not md5 size mtime) %{old_logfile}
%endif
%config(noreplace) %{logrotateddir}/%{daemon_name}

%if %{with oqgraph}
%files oqgraph
%config(noreplace) %{_sysconfdir}/my.cnf.d/oqgraph.cnf
%{_libdir}/mysql/plugin/ha_oqgraph.so
%endif


%if %{with devel}
%files devel
%{_bindir}/mysql_config*
%{_includedir}/mysql
%{_datadir}/aclocal/mysql.m4
%{_libdir}/mysql/libmysqlclient.so
%{_libdir}/mysql/libmysqlclient_r.so
%{_mandir}/man1/mysql_config.1*
%endif

%if %{with embedded}
%files embedded
%{_libdir}/mysql/libmysqld.so.*

%files embedded-devel
%{_libdir}/mysql/libmysqld.so
%{_bindir}/mysql_client_test_embedded
%{_bindir}/mysqltest_embedded
%{_mandir}/man1/mysql_client_test_embedded.1*
%{_mandir}/man1/mysqltest_embedded.1*
%endif

%if %{with bench}
%files bench
%{_datadir}/sql-bench
%endif

%if %{with test}
%files test
%{_bindir}/mysql_client_test
%{_bindir}/my_safe_process
%attr(-,mysql,mysql) %{_datadir}/mysql-test
%{_mandir}/man1/mysql_client_test.1*
%endif


%changelog
* Tue Jan 30 2018 Ben Harper <ben.harper@rackspace.com> - 1:10.0.34-1.ius
- Latest upstream

* Tue Oct 31 2017 Ben Harper <ben.harper@rackspace.com> - 1:10.0.33-1.ius
- Latest upstream
- remove Patch2, addressed upstream
- update Patch8

* Tue Aug 08 2017 Ben Harper <ben.harper@rackspace.com> - 1:10.0.32-1.ius
- Latest upstream
- remove Patch34, patched upstream

* Wed May 31 2017 Carl George <carl.george@rackspace.com> - 1:10.0.31-2.ius
- More clean up of provides, conflicts, and requires
- Filter provides in el6 properly (Fedora)
- JdbcMariaDB.jar test removed (Fedora)
- BR multilib-rpm-config and use it for multilib workarounds (Fedora)
- Sync mysql-prepare-db-dir.sh with Fedora
- Add explicit EVR requirement in main package for -libs rhbz#1406320 (Fedora)
- Embedded-devel should require libaio-devel rhbz#1290517 (Fedora)
- Fix paths in mysql_install_db script rhbz#1134328 (Fedora)
- Add missing build requires
- Do not create test database by default rhbz#1194611 (Fedora)
- Sync test suite with Fedora

* Thu May 25 2017 Carl George <carl.george@rackspace.com> - 1:10.0.31-1.ius
- Latest upstream
- Remove obsoletes
- Set %%old_logfile macro
- Clean up provides and conflicts
- Macro clean up
- Remove patch31, resolved upstream (MDEV-6262)
- Remove jemalloc buildrequirement, not needed
- Add BuildRequires selinux-policy-devel
- Fix license handling

* Thu Mar 09 2017 Ben Harper <ben.harper@rackspace.com> - 1:10.0.30-1.ius
- Latest upstream
- update Patch4

* Fri Jan 13 2017 Ben Harper <ben.harper@rackspace.com> - 1:10.0.29-1.ius
- Latest upstream
- add new file, /usr/bin/mysqld_safe_helper
- tweak to some docs deletion

* Tue Nov 01 2016 Carl George <carl.george@rackspace.com> - 1:10.0.28-1.ius
- Latest upstream

* Thu Aug 25 2016 Ben Harper <ben.harper@rackspace.com> - 1:10.0.27-1.ius
- Latest upstream

* Mon Jun 27 2016 Ben Harper <ben.harper@rackspace.com> - 1:10.0.26-1.ius
- Latest upstream
- update Source107 to skip main.multi_update
- update Source12
  from http://pkgs.fedoraproject.org/cgit/rpms/mariadb.git/commit/?id=cb04c7ab875698414cfd3be4040e52630380eb95

* Mon May 02 2016 Ben Harper <ben.harper@rackspace.com> - 1:10.0.25-1.ius
- Latest upstream
- update Patch2
- disable Patch36, appears to be no longer needed

* Tue Feb 23 2016 Carl George <carl.george@rackspace.com> - 1:10.0.24-1.ius
- Latest upstream
- Add main.ssl_cert_verify test to skip list

* Fri Jan 08 2016 Ben Harper <ben.harper@rackspace.com> - 1:10.0.23-2.ius
- provide mysql-compat-server and not mysql-server, see GH#2

* Tue Dec 22 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.23-1.ius
- Latest upstream
- disable Patch33

* Fri Oct 30 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.22-1.ius
- Latest upstream

* Tue Aug 11 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.21-2.ius
- Update Patch34

* Fri Aug 07 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.21-1.ius
- Latest upstream
- Update Patch34

* Fri Jun 19 2015 Carl George <carl.george@rackspace.com> - 1:10.0.20-1.ius
- Latest upstream
- Add ssl_7937 test to skip list

* Wed May 13 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.19-1.ius
- Latest upstream
- add Source107
- disable Patch5 and Patch7
- update Patch36 to match Fedora, http://pkgs.fedoraproject.org/cgit/mariadb.git/tree/mariadb-ssltest.patch?id=965e4581ba120efdfe2bfcb9846b1e9c89bd2424

* Mon Mar 02 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.17-1.ius
- Latest upstream
- remove Source100-106 and Patch100, patched upstream

* Wed Jan 28 2015 Ben Harper <ben.harper@rackspace.com> - 1:10.0.16-1.ius
- Latest upstream
- add Source100-106 and Patch100 to correct expired CA certificate
- add Provides for config(mariadb-libs)

* Wed Nov 26 2014 Carl George <carl.george@rackspace.com> - 1:10.0.15-1.ius
- Latest upstream
- Refresh patch5
- Include new files mroonga/install.sql and mroonga/uninstall.sql

* Mon Oct 06 2014 Ben Harper <ben.harper@rackspace.com> - 1:10.0.14-1.ius
- Latest upstream
- add buildrequires for jemalloc-devel and -DWITH_JEMALLOC=auto
- change how INFO_SRC INFO_BIN get installed
- update to use %{epoch}

* Tue Sep 16 2014 Ben Harper <ben.harper@rackspace.com> - 1:10.0.13-4.ius
- more tweaks to Conflicts

* Mon Sep 15 2014 Ben Harper <ben.harper@rackspace.com> - 1:10.0.13-3
- readding epoch as conflicts were not working correctly

* Thu Sep 04 2014 Ben Harper <ben.harper@rackspace.com> - 10.0.13-2
- tweaking and adding Conflicts, Requires and Provides

* Tue Aug 26 2014 Ben Harper <ben.harper@rackspace.com> - 10.0.13-1
- inital port from fedora SRPM

* Tue Aug 19 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.13-4
- Build config subpackage everytime
- Disable failing tests: innodb_simulate_comp_failures_small, key_cache
  rhbz#1096787

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.0.13-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Aug 14 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.13-2
- Include mysqld_unit only if required; enable tokudb in f20-

* Wed Aug 13 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.13-1
- Rebase to version 10.0.13

* Tue Aug 12 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.12-8
- Introduce -config subpackage and ship base config files here

* Tue Aug  5 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.12-7
- Adopt changes from mysql, thanks Bjorn Munch <bjorn.munch@oracle.com>

* Mon Jul 28 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.12-6
- Use explicit sysconfdir
- Absolut path for default value for pid file and error log

* Tue Jul 22 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.12-5
- Hardcoded paths removed to work fine in chroot
- Spec rewrite to be more similar to oterh MySQL implementations
- Use variable for daemon unit name
- Include SysV init script if built on older system
- Add possibility to not ship some sub-packages

* Mon Jul 21 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.12-4
- Reformating spec and removing unnecessary snippets

* Tue Jul 15 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.12-3
- Enable OQGRAPH engine and package it as a sub-package
- Add support for TokuDB engine for x86_64 (currently still disabled)
- Re-enable tokudb_innodb_xa_crash again, seems to be fixed now
- Drop superfluous -libs and -embedded ldconfig deps (thanks Ville Skyttä)
- Separate -lib and -common sub-packages
- Require /etc/my.cnf instead of shipping it
- Include README.mysql-cnf
- Multilib support re-worked
- Introduce new option with_mysqld_unit
- Removed obsolete mysql-cluster, the package should already be removed
- Improve error message when log file is not writable
- Compile all binaries with full RELRO (RHBZ#1092548)
- Use modern symbol filtering with compatible backup
- Add more groupnames for server's my.cnf
- Error messages now provided by a separate package (thanks Alexander Barkov)
- Expand paths in helper scripts using cmake

* Wed Jun 18 2014 Mikko Tiihonen <mikko.tiihonen@iki.fi> - 1:10.0.12-2
- Use -fno-delete-null-pointer-checks to avoid segfaults with gcc 4.9

* Tue Jun 17 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.12-1
- Rebase to version 10.0.12

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.0.11-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun  3 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.11-4
- rebuild with tests failing on different arches disabled (#1096787)

* Thu May 29 2014 Dan Horák <dan[at]danny.cz> - 1:10.0.11-2
- rebuild with tests failing on big endian arches disabled (#1096787)

* Wed May 14 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.11-1
- Rebase to version 10.0.11

* Mon May 05 2014 Honza Horak <hhorak@redhat.com> - 1:10.0.10-3
- Script for socket check enhanced

* Thu Apr 10 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.10-2
- use system pcre library

* Thu Apr 10 2014 Jakub Dorňák <jdornak@redhat.com> - 1:10.0.10-1
- Rebase to version 10.0.10

* Wed Mar 12 2014 Honza Horak <hhorak@redhat.com> - 1:5.5.36-2
- Server crashes on SQL select containing more group by and left join statements using innodb tables
  Resolves: #1065676
- Fix paths in helper scripts
- Move language files into mariadb directory

* Thu Mar 06 2014 Honza Horak <hhorak@redhat.com> - 1:5.5.36-1
- Rebase to 5.5.36
  https://kb.askmonty.org/en/mariadb-5536-changelog/

* Tue Feb 25 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-5
- Daemon helper scripts sanity changes and spec files clean-up

* Tue Feb 11 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-4
- Fix typo in mysqld.service
  Resolves: #1063981

* Wed Feb  5 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-3
- Do not touch the log file in post script, so it does not get wrong owner
  Resolves: #1061045

* Thu Jan 30 2014 Honza Horak <hhorak@redhat.com> 1:5.5.35-1
- Rebase to 5.5.35
  https://kb.askmonty.org/en/mariadb-5535-changelog/
  Also fixes: CVE-2014-0001, CVE-2014-0412, CVE-2014-0437, CVE-2013-5908,
  CVE-2014-0420, CVE-2014-0393, CVE-2013-5891, CVE-2014-0386, CVE-2014-0401,
  CVE-2014-0402
  Resolves: #1054043
  Resolves: #1059546

* Tue Jan 14 2014 Honza Horak <hhorak@redhat.com> - 1:5.5.34-9
- Adopt compatible system versioning
  Related: #1045013
- Use compatibility mysqld.service instead of link
  Related: #1014311

* Mon Jan 13 2014 Rex Dieter <rdieter@fedoraproject.org> 1:5.5.34-8
- move mysql_config alternatives scriptlets to -devel too

* Fri Jan 10 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-7
- Build with -O3 on ppc64
  Related: #1051069
- Move mysql_config to -devel sub-package and remove Require: mariadb
  Related: #1050920

* Fri Jan 10 2014 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 1:5.5.34-6
- Disable main.gis-precise test also for AArch64
- Disable perfschema.func_file_io and perfschema.func_mutex for AArch64
  (like it is done for 32-bit ARM)

* Fri Jan 10 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-5
- Clean all non-needed doc files properly

* Wed Jan  8 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-4
- Read socketfile location in mariadb-prepare-db-dir script

* Mon Jan  6 2014 Honza Horak <hhorak@redhat.com> 1:5.5.34-3
- Don't test EDH-RSA-DES-CBC-SHA cipher, it seems to be removed from openssl
  which now makes mariadb/mysql FTBFS because openssl_1 test fails
  Related: #1044565
- Use upstream's layout for symbols version in client library
  Related: #1045013
- Check if socket file is not being used by another process at a time
  of starting the service
  Related: #1045435
- Use %%ghost directive for the log file
  Related: 1043501

* Wed Nov 27 2013 Honza Horak <hhorak@redhat.com> 1:5.5.34-2
- Fix mariadb-wait-ready script

* Fri Nov 22 2013 Honza Horak <hhorak@redhat.com> 1:5.5.34-1
- Rebase to 5.5.34

* Mon Nov  4 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-4
- Fix spec file to be ready for backport by Oden Eriksson
  Resolves: #1026404

* Mon Nov  4 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-3
- Add pam-devel to build-requires in order to build
  Related: #1019945
- Check if correct process is running in mysql-wait-ready script
  Related: #1026313

* Mon Oct 14 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-2
- Turn on test suite

* Thu Oct 10 2013 Honza Horak <hhorak@redhat.com> 1:5.5.33a-1
- Rebase to 5.5.33a
  https://kb.askmonty.org/en/mariadb-5533-changelog/
  https://kb.askmonty.org/en/mariadb-5533a-changelog/
- Enable outfile_loaddata test
- Disable tokudb_innodb_xa_crash test

* Mon Sep  2 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-12
- Re-organize my.cnf to include only generic settings
  Resolves: #1003115
- Move pid file location to /var/run/mariadb
- Make mysqld a symlink to mariadb unit file rather than the opposite way
  Related: #999589

* Thu Aug 29 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-11
- Move log file into /var/log/mariadb/mariadb.log
- Rename logrotate script to mariadb
- Resolves: #999589

* Wed Aug 14 2013 Rex Dieter <rdieter@fedoraproject.org> 1:5.5.32-10
- fix alternatives usage

* Tue Aug 13 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-9
- Multilib issues solved by alternatives
  Resolves: #986959

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 1:5.5.32-8
- Perl 5.18 rebuild

* Wed Jul 31 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-7
- Do not use login shell for mysql user

* Tue Jul 30 2013 Honza Horak <hhorak@redhat.com> - 1:5.5.32-6
- Remove unneeded systemd-sysv requires
- Provide mysql-compat-server symbol
- Create mariadb.service symlink
- Fix multilib header location for arm
- Enhance documentation in the unit file
- Use scriptstub instead of links to avoid multilib conflicts
- Add condition for doc placement in F20+

* Sun Jul 28 2013 Dennis Gilmore <dennis@ausil.us> - 1:5.5.32-5
- remove "Requires(pretrans): systemd" since its not possible
- when installing mariadb and systemd at the same time. as in a new install

* Sat Jul 27 2013 Kevin Fenzi <kevin@scrye.com> 1:5.5.32-4
- Set rpm doc macro to install docs in unversioned dir

* Fri Jul 26 2013 Dennis Gilmore <dennis@ausil.us> 1:5.5.32-3
- add Requires(pre) on systemd for the server package

* Tue Jul 23 2013 Dennis Gilmore <dennis@ausil.us> 1:5.5.32-2
- replace systemd-units requires with systemd
- remove solaris files

* Fri Jul 19 2013 Honza Horak <hhorak@redhat.com> 1:5.5.32-1
- Rebase to 5.5.32
  https://kb.askmonty.org/en/mariadb-5532-changelog/
- Clean-up un-necessary systemd snippets

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1:5.5.31-7
- Perl 5.18 rebuild

* Mon Jul  1 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-6
- Test suite params enhanced to decrease server condition influence
- Fix misleading error message when uninstalling built-in plugins
  Related: #966873

* Thu Jun 27 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-5
- Apply fixes found by Coverity static analysis tool

* Wed Jun 19 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-4
- Do not use pretrans scriptlet, which doesn't work in anaconda
  Resolves: #975348

* Fri Jun 14 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-3
- Explicitly enable mysqld if it was enabled in the beginning
  of the transaction.

* Thu Jun 13 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-2
- Apply man page fix from Jan Stanek

* Fri May 24 2013 Honza Horak <hhorak@redhat.com> 1:5.5.31-1
- Rebase to 5.5.31
  https://kb.askmonty.org/en/mariadb-5531-changelog/
- Preserve time-stamps in case of installed files
- Use /var/tmp instead of /tmp, since the later is using tmpfs,
  which can cause problems
  Resolves: #962087
- Fix test suite requirements

* Sun May  5 2013 Honza Horak <hhorak@redhat.com> 1:5.5.30-2
- Remove mytop utility, which is packaged separately
- Resolve multilib conflicts in mysql/private/config.h

* Fri Mar 22 2013 Honza Horak <hhorak@redhat.com> 1:5.5.30-1
- Rebase to 5.5.30
  https://kb.askmonty.org/en/mariadb-5530-changelog/

* Fri Mar 22 2013 Honza Horak <hhorak@redhat.com> 1:5.5.29-11
- Obsolete MySQL since it is now renamed to community-mysql
- Remove real- virtual names

* Thu Mar 21 2013 Honza Horak <hhorak@redhat.com> 1:5.5.29-10
- Adding epoch to have higher priority than other mysql implementations
  when comes to provider comparison

* Wed Mar 13 2013 Honza Horak <hhorak@redhat.com> 5.5.29-9
- Let mariadb-embedded-devel conflict with MySQL-embedded-devel
- Adjust mariadb-sortbuffer.patch to correspond with upstream patch

* Mon Mar  4 2013 Honza Horak <hhorak@redhat.com> 5.5.29-8
- Mask expected warnings about setrlimit in test suite

* Thu Feb 28 2013 Honza Horak <hhorak@redhat.com> 5.5.29-7
- Use configured prefix value instead of guessing basedir
  in mysql_config
  Resolves: #916189
- Export dynamic columns and non-blocking API functions documented
  by upstream

* Wed Feb 27 2013 Honza Horak <hhorak@redhat.com> 5.5.29-6
- Fix sort_buffer_length option type

* Wed Feb 13 2013 Honza Horak <hhorak@redhat.com> 5.5.29-5
- Suppress warnings in tests and skip tests also on ppc64p7

* Tue Feb 12 2013 Honza Horak <hhorak@redhat.com> 5.5.29-4
- Suppress warning in tests on ppc
- Enable fixed index_merge_myisam test case

* Thu Feb 07 2013 Honza Horak <hhorak@redhat.com> 5.5.29-3
- Packages need to provide also %%_isa version of mysql package
- Provide own symbols with real- prefix to distinguish from mysql
  unambiguously
- Fix format for buffer size in error messages (MDEV-4156)
- Disable some tests that fail on ppc and s390
- Conflict only with real-mysql, otherwise mariadb conflicts with ourself

* Tue Feb 05 2013 Honza Horak <hhorak@redhat.com> 5.5.29-2
- Let mariadb-libs to own /etc/my.cnf.d

* Thu Jan 31 2013 Honza Horak <hhorak@redhat.com> 5.5.29-1
- Rebase to 5.5.29
  https://kb.askmonty.org/en/mariadb-5529-changelog/
- Fix inaccurate default for socket location in mysqld-wait-ready
  Resolves: #890535

* Thu Jan 31 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-8
- Enable obsoleting mysql

* Wed Jan 30 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-7
- Adding necessary hacks for perl dependency checking, rpm is still
  not wise enough
- Namespace sanity re-added for symbol default_charset_info

* Mon Jan 28 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-6
- Removed %%{_isa} from provides/obsoletes, which doesn't allow
  proper obsoleting
- Do not obsolete mysql at the time of testing

* Thu Jan 10 2013 Honza Horak <hhorak@redhat.com> 5.5.28a-5
- Added licenses LGPLv2 and BSD
- Removed wrong usage of %%{epoch}
- Test-suite is run in %%check
- Removed perl dependency checking adjustment, rpm seems to be smart enough
- Other minor spec file fixes

* Tue Dec 18 2012 Honza Horak <hhorak@redhat.com> 5.5.28a-4
- Packaging of MariaDB based on MySQL package

