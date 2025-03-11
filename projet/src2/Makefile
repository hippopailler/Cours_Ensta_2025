include Make_linux.inc
#include Make_msys2.inc
#include Make_osx.inc

# Assurez-vous que MPI est installé sur votre machine et définissez les chemins si nécessaire.
# Si vous utilisez mpic++, il faut remplacer $(CXX) par mpic++
CXX = mpic++

CXXFLAGS = -std=c++17 -Wall
ifdef DEBUG
CXXFLAGS += -g -O0 -fbounds-check -pedantic -D_GLIBCXX_DEBUG -fsanitize=address
else
CXXFLAGS += -O3 -march=native
endif

# Ajoutez ici les flags pour inclure les bibliothèques MPI.
# Si votre installation de MPI nécessite des chemins spécifiques, vous pouvez les ajouter ici.
# Par exemple, si MPI est installé à /usr/local/include et /usr/local/lib, vous ajouteriez :
# CXXFLAGS += -I/usr/local/include
# LIB += -L/usr/local/lib -lmpi

ALL = simulation.exe 

default:	help

all: $(ALL)

clean:
	@rm -fr *.o *.exe *~ *.d

.cpp.o:
	$(CXX) $(CXXFLAGS) -MMD -c $< -o $@

# Assurez-vous de lier les bibliothèques MPI ici.
simulation.exe : display.o model.o simulation.o
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LIB) -lmpi  # Liez la bibliothèque MPI ici.

help:
	@echo "Available targets : "
	@echo "    all            : compile all executables"
	@echo "Add DEBUG=yes to compile in debug"
	@echo "Configuration :"
	@echo "    CXX      :    $(CXX)"
	@echo "    CXXFLAGS :    $(CXXFLAGS)"

%.html: %.md
	pandoc -s --toc $< --css=./github-pandoc.css --metadata pagetitle="OS202 - TD1" -o $@

-include *.d