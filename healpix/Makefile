

scene.scad: scene.py Makefile
	python scene.py > scene.scad

scene.py: healball ./src/scene_py.py Makefile
	./healball 8 > scene_c.py
	cat scene_c.py ./src/scene_py.py > scene.py

healball: ./src/healball.c ./src/chealpix.c Makefile
	gcc -o healball -I./src ./src/chealpix.c ./src/healball.c -lm
