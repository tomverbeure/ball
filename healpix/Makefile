

scene.scad: scene.py Makefile
	python scene.py > scene.scad

scene.py: healball Makefile
	./healball 16 > scene.py

healball: ./src/healball.c ./src/chealpix.c Makefile
	gcc -o healball -I./src ./src/chealpix.c ./src/healball.c -lm
