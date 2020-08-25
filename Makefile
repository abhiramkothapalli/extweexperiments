all:
	$(MAKE) -C src
	$(MAKE) -C network

clean:
	$(MAKE) -C src clean
	$(MAKE) -C network clean
