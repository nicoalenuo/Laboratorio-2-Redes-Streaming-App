@echo off
setlocal enabledelayedexpansion

set n=10  REM Set 'n' to the number of times you want to execute the commands

start cmd /k "python code/server.py 127.0.0.1 2023"
start cmd /k"vlc -vvv prueba2.mp4 --sout "#transcode{vcodec=mp4v,acodec=mpga}:rtp{proto=udp,mux=ts,dst=127.0.0.1,port=9999}" --loop --ttl 1"

for /l %%i in (1,1,%n%) do (
    set /a port=2022+%%i
    
    start cmd /k "vlc rtp://127.0.0.1:!port!" 
    start cmd /k "python code/cliente.py 127.0.0.1 2023 !port!"
)

endlocal
