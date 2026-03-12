@echo on
echo Creating virtual environment...
py -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt


echo Running pytest...
python -m pytest -v

echo Done.

