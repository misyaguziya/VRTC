pyinstaller --onedir --onefile --windowed --clean --icon="./img/vrct_logo_mark_black.ico" --add-data "./img;img/" --name VRCT --exclude-module numpy --exclude-module pandas --exclude-module matplotlib --exclude-module PyQt5 main.py