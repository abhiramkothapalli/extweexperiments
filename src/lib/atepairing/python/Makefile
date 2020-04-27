TARGET += gfeccore.py

all:$(TARGET)

wrap:
	python3 setup.py build_ext -i

CPP_FLAGS=-DCPP -I../include 
LD_FLAGS=-lzm -L../lib 

gfeccore: gfeccore.cpp gfeccore.h 
	g++ $(CPP_FLAGS) $(LD_FLAGS) -o gfeccore gfeccore.cpp 

gfeccore.py: gfeccore gfeccore.i
	swig -python -c++ gfeccore.i
	cc -c `python3-config --cflags` $(CPP_FLAGS) gfeccore.cpp gfeccore_wrap.cxx 
	g++ -bundle `python3-config --ldflags` $(LD_FLAGS) gfeccore.o gfeccore_wrap.o -o _gfeccore.so



clean:
	rm gfeccore
	rm gfeccore.py


	rm *.o
	rm *.so
	rm *.cxx
