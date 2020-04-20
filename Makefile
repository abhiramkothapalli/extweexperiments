all:
	pip3 install Pyro4
	$(MAKE) -C src

clean:
	$(MAKE) -C src clean
