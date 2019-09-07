
all: healball
	./healball 2

healball: ./src/healball.c
	gcc -o healball -I Healpix_3.50/src/C/subs/ -lm Healpix_3.50/src/C/subs/chealpix.c ./src/healball.c

