n=5

gnome-terminal -- bash -c "python code/server.py 127.0.0.1 2023"

gnome-terminal -- bash -c "cvlc -vvv prueba2.mp4 --sout '#transcode{vcodec=mp4v,acodec=mpga}:rtp{proto=udp,mux=ts,dst=127.0.0.1,port=9999}' --loop --ttl 1"

for ((i=1; i<=n; i++)); do
    port=$((2022+i))
    
    gnome-terminal -- bash -c "cvlc rtp://127.0.0.1:$port"
    gnome-terminal -- bash -c "python code/cliente.py 127.0.0.1 2023 $port"
done
