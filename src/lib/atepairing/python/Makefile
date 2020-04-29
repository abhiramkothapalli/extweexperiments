TARGET += gfeccore.py

all:$(TARGET)

gfeccore.py: gfeccore.i
	python3 setup.py build_ext --inplace


clean:
	rm -f gfeccore
	rm -f gfeccore.py
	rm -f gfeccore_wrap.*


	rm -f *.o
	rm -f *.so
	rm -f *.cxx
