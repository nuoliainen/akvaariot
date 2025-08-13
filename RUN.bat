@echo off

if exist "venv\" (
	echo Activating virtual environment...
	call venv\Scripts\activate
)

if not exist "venv\" (
	echo Creating and activating virtual environment...
	python -m venv venv
	call venv\Scripts\activate
	pip install flask
	python.exe -m pip install --upgrade pip
)

if not exist "database.db" (
	echo Initializing database.db...
	sqlite3 database.db < schema.sql
	sqlite3 database.db < init.sql
)

echo Opening app...
flask run
