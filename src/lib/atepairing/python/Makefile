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
	rm -f gfeccore
	rm -f gfeccore.py


	rm -f *.o
	rm -f *.so
	rm -f *.cxx

# include ../common.mk

# HEADER = ../include/zm.h ../include/bn.h ../include/zm2.h test_point.hpp
# TARGET = gfeccore.py bn ../lib/libzm.a


# all:$(TARGET)

# .SUFFIXES: .cpp

# gfeccore: gfeccore.o ../lib/libzm.a
# 	$(CXX) -o $@ $< $(LDFLAGS) $(BIT)

# gfeccore.py: gfeccore gfeccore.i
# 	swig -python -c++ gfeccore.i
# 	cc -c `python3-config --cflags` $(CPP_FLAGS) gfeccore.cpp gfeccore_wrap.cxx 
# 	g++ -bundle `python3-config --ldflags` $(LD_FLAGS) gfeccore.o gfeccore_wrap.o -o _gfeccore.so

# bn: bn.o ../lib/libzm.a
# 	$(CXX) -o $@ $< $(LDFLAGS) $(BIT)

# ../lib/libzm.a: $(HEADER) ../src/zm2.cpp ../src/zm.cpp
# 	$(MAKE) -C ../src ../lib/libzm.a


# bn.o: bn.cpp $(HEADER)
# gfeccore.o: gfeccore.cpp gfeccore.h $(HEADER)







# clean:
# 	rm -f gfeccore.py
# 	rm -f gfeccore_wrap.c
# 	rm -f gfeccore_wrap.cxx


# 	rm -f *.o
# 	rm -f *.so
# 	rm -f *.cxx

# 	rm -f gfeccore

