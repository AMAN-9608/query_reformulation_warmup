#!/bin/bash

pip install -r requirements.txt

python warmup_api.py & streamlit run warmup_frontend.py