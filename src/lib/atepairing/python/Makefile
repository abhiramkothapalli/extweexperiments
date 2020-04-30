TARGET += gfeccore.py
TARGET += gfeccore

all:$(TARGET)


CPP_FLAGS=-DCPP -I../include 
LD_FLAGS=-lzm -L../lib

gfeccore: gfeccore.cpp gfeccore.h 
	g++ $(CPP_FLAGS) $(LD_FLAGS) -o gfeccore gfeccore.cpp 

gfeccore.py: gfeccore.i gfeccore.cpp gfeccore.h
	python3 setup.py build_ext --inplace


clean:
	rm -f gfeccore
	rm -f gfeccore.py
	rm -f gfeccore_wrap.*


	rm -f *.o
	rm -f *.so
	rm -f *.cxx
