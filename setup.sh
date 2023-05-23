# create virtual environment
python3 -m venv assignment5_env

# activate virtual environment
source ./assignment5_env/bin/activate

# update pip, install requirements
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install git+https://github.com/TalkBank/TBDBpy.git
python3 -m spacy download en_core_web_md