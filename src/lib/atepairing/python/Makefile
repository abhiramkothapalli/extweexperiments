TARGET += wrap

all:$(TARGET)

wrap:
	python3 setup.py build_ext -i

CPP_FLAGS=-DCPP -I../include 
LD_FLAGS=-lzm -L../lib

example: example.cpp example.h 
	g++ $(CPP_FLAGS) $(LD_FLAGS) -o example example.cpp 

example.py: example example.i
	swig -python -c++ example.i
	cc -c `python-config --cflags` $(CPP_FLAGS) example.cpp example_wrap.cxx 
	g++ -bundle `python-config --ldflags` $(LD_FLAGS) example.o example_wrap.o -o _example.so


clean:
	rm *.so
