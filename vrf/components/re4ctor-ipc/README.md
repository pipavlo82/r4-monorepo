# R4 Secure MVP (Socket Client SDK)

Клієнтський SDK (C/Python) читає байти через Unix-socket.
Серверне ядро (твій RNG) — окремо і не розкривається.

Socket: /run/r4sock/r4.sock
Протокол: proto/README.md

## Збірка
make

## Smoke (локально, з мок-сервером)
sudo groupadd -f r4users
sudo usermod -aG r4users $USER   # перелогінитись у нову shell-сесію
sudo -E env PATH="$PATH" python3 bin/r4_server_mock.py &
./bin/r4cat -n 64 -hex
python3 bindings/python/r4.py
