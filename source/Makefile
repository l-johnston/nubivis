BOOST_DIR = /usr/local/boost_1_78_0
CXXFLAGS = -Wall -I$(BOOST_DIR)
CXX = g++
pe : parser.o pe.o
	$(CXX) $(CXXFLAGS) -o pe parser.o pe.o
clean :
	rm -f pe parser.o pe.o
debug : CXXFLAGS += -g
debug : pe
