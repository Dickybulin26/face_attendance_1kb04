#!/bin/bash

#* Run the app localy

# Check python version
python -V

# Check pip version
pip -V

python.exe -m pip install --upgrade pip

pip install virtualenv

# Create virtual environment
python -m venv venv

# Activate virtual environment For Windows, Linux, and Mac
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    if [ $? -eq 0 ]; then
        echo "Virtual environment activated for Windows"
    else
        echo "Failed to activate virtual environment for Windows"
        exit 1
    fi
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    if [ $? -eq 0 ]; then
        echo "Virtual environment activated for Linux/Mac"
    else
        echo "Failed to activate virtual environment for Linux/Mac"
        exit 1
    fi
fi


python.exe -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# install face_recognition_models
pip install git+https://github.com/ageitgey/face_recognition_models

# check installed packages
pip list

# Setup Frontend
npm install
npm run build

# Run the app
python app.py