vlc -vvv prueba2.mp4 --sout "#transcode{vcodec=mp4v,acodec=mpga}:rtp{proto=udp,mux=ts,dst=127.0.0.1,port=9999}" --loop --ttl 1