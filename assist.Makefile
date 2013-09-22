.PHONY: deps

deps:
	curl -O https://leveldb.googlecode.com/files/leveldb-1.14.0.tar.gz
	tar xvf leveldb-1.14.0.tar.gz
	$(MAKE) -C leveldb-1.14.0 all
	sudo cp -R leveldb-1.14.0/include/leveldb /usr/include
	sudo cp leveldb-1.14.0/libleveldb.so* /usr/lib
