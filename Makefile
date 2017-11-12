PREFIX = '/usr'
DESTDIR = ''
TEMPDIR := $(shell mktemp -u --suffix .qfortune)
PROGRAM_NAME := $(shell grep ^PROGRAM_NAME src/qfortune.py | cut -d\" -f2)
EXECUTABLE_NAME := $(shell grep ^EXECUTABLE_NAME src/qfortune.py | cut -d\" -f2)
DESCRIPTION := $(shell grep ^DESCRIPTION src/qfortune.py | cut -d\" -f2)
VERSION := $(shell grep ^VERSION src/qfortune.py | cut -d\" -f2)
AUTHOR := $(shell grep ^AUTHOR src/qfortune.py | cut -d\" -f2)
MAIL := $(shell grep ^MAIL src/qfortune.py | cut -d\" -f2)
LICENSE := $(shell grep ^LICENSE src/qfortune.py | cut -d\" -f2)
TIMESTAMP = $(shell LC_ALL=C date '+%a, %d %b %Y %T %z')

documents: ChangeLog mo

mo: po/es_ES.mo po/es.mo

po/es_ES.mo: po/es_ES.po
	msgfmt $^ -o $@

po/es.mo: po/es.po
	msgfmt $^ -o $@

pot: messages.pot

messages.pot: src/qfortune.py
	pygettext3 $^

ChangeLog: changelog.in
	@echo "$(EXECUTABLE_NAME) ($(VERSION)) unstable; urgency=medium" > $@
	@echo >> $@
	@echo "  * Git build." >> $@
	@echo >> $@
	@echo " -- $(AUTHOR) <$(MAIL)>  $(TIMESTAMP)" >> $@
	@echo >> $@
	@cat $^ >> $@

install: documents
	install -Dm 755 src/qfortune.py $(DESTDIR)/$(PREFIX)/bin/qfortune
	install -Dm 644 LICENSE $(DESTDIR)/$(PREFIX)/share/licenses/qfortune/COPYING
	install -Dm 644 README.md $(DESTDIR)/$(PREFIX)/share/doc/qfortune/README
	install -Dm 644 ChangeLog $(DESTDIR)/$(PREFIX)/share/doc/qfortune/ChangeLog
	install -Dm 644 resources/qfortune.desktop $(DESTDIR)/$(PREFIX)/share/applications/qfortune.desktop
	install -Dm 644 resources/qfortune.svg $(DESTDIR)/$(PREFIX)/share/pixmaps/qfortune.svg
	install -Dm 644 po/es.mo $(DESTDIR)/$(PREFIX)/share/locale/es/LC_MESSAGES/qfortune.mo
	install -Dm 644 po/es_ES.mo $(DESTDIR)/$(PREFIX)/share/locale/es_ES/LC_MESSAGES/qfortune.mo
	install -d -m 755 $(DESTDIR)/$(PREFIX)/share/qfortune
	cp -r resources/fortunes $(DESTDIR)/$(PREFIX)/share/qfortune
	chown -R root:root $(DESTDIR)/$(PREFIX)/share/qfortune
	chmod -R u=rwX,go=rX $(DESTDIR)/$(PREFIX)/share/qfortune

uninstall:
	rm -f $(PREFIX)/bin/qfortune
	rm -f $(PREFIX)/share/locale/es/LC_MESSAGES/qfortune.mo
	rm -f $(PREFIX)/share/locale/es_ES/LC_MESSAGES/qfortune.mo
	rm -rf $(PREFIX)/share/licenses/qfortune/
	rm -rf $(PREFIX)/share/doc/qfortune/
	rm -rf $(PREFIX)/share/qfortune/

clean:
	rm -rf *.xz *.gz *.pot po/*.mo *.tgz *.deb *.rpm ChangeLog /tmp/tmp.*.qfortune debian/changelog debian/README debian/files debian/qfortune debian/debhelper-build-stamp debian/qfortune*


pkg: clean
	mkdir $(TEMPDIR)
	tar cf $(TEMPDIR)/qfortune.tar ../qfortune
	cp packages/pacman/local/PKGBUILD $(TEMPDIR)/
	cd $(TEMPDIR); makepkg
	cp $(TEMPDIR)/qfortune-*.pkg.tar.xz .
	@echo Package done!
	@echo You can install it as root with:
	@echo pacman -U qfortune-*.pkg.tar.xz

deb: ChangeLog mo
	cp README.md debian/README
	cp ChangeLog debian/changelog
	#fakeroot debian/rules clean
	#fakeroot debian/rules build
	fakeroot debian/rules binary
	mv ../qfortune_$(VERSION)_all.deb .
	@echo Package done!
	@echo You can install it as root with:
	@echo dpkg -i qfortune_$(VERSION)_all.deb
