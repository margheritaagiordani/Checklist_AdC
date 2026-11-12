@echo off
title Avvio Scheda Osservazione Vela
echo Avvio del server in corso...
call "C:\Users\margh\miniconda3\Scripts\activate.bat" vela_env
python -m streamlit run app.py
pause
