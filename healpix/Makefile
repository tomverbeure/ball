

scene.scad: scene.py Makefile
	python scene.py > scene.scad

scene.py: healball Makefile
	./healball 4 > scene.py

healball: ./src/healball.c Makefile
	gcc -o healball -I Healpix_3.50/src/C/subs/ Healpix_3.50/src/C/subs/chealpix.c ./src/healball.c -lm
