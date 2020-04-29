include ../common.mk

HEADER= ../include/zm.h ../include/bn.h ../include/zm2.h test_point.hpp

TARGET += gfeccore.py bn ../lib/libzm.a

all:$(TARGET)

.SUFFIXES: .cpp

CPP_FLAGS=-DCPP -I../include
LD_FLAGS=-lzm -L../lib 

gfeccore.py: gfeccore gfeccore.i
	swig -python -c++ gfeccore.i
	cc -c `python3-config --cflags` $(CPP_FLAGS) gfeccore.cpp gfeccore_wrap.cxx 
	g++ -bundle `python3-config --ldflags` $(LD_FLAGS) gfeccore.o gfeccore_wrap.o -o _gfeccore.so

gfeccore: gfeccore.o ../lib/libzm.a
	$(CXX) -o $@ $< $(LDFLAGS) $(BIT)

bn: bn.o ../lib/libzm.a
	$(CXX) -o $@ $< $(LDFLAGS) $(BIT)

../lib/libzm.a: $(HEADER) ../src/zm2.cpp ../src/zm.cpp
	$(MAKE) -C ../src ../lib/libzm.a

gfeccore.o: gfeccore.cpp $(HEADER)
bn.o: bn.cpp $(HEADER)

clean:
	rm -f gfeccore
	rm -f gfeccore.py


	rm -f *.o
	rm -f *.so
	rm -f *.cxx


