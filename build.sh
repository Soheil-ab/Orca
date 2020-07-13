g++ -pthread src/orca-server-mahimahi.cc src/flow.cc -o orca-server-mahimahi
g++ src/client.c -o client
cp client rl-module/
mv orca-server*  rl-module/
sudo chmod +x rl-module/client
sudo chmod +x rl-module/orca-server-mahimahi


