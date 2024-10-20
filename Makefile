all: clean build


build:
	@echo "Building executable"
	pyinstaller main.py -F -c -n QueVinchik --clean --noupx

clean:
	@echo "Cleaning old files"
	rm -rf ./QueVinchik.spec
	rm -rf ./dist
	rm -rf ./build
