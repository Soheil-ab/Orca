sudo sysctl -q net.ipv4.tcp_wmem="4096 32768 4194304" #Doubling the default value from 16384 to 32768
sudo sysctl -w -q net.ipv4.tcp_low_latency=1
sudo sysctl -w -q net.ipv4.tcp_autocorking=0
sudo sysctl -w -q net.ipv4.tcp_no_metrics_save=1
sudo sysctl -w -q net.ipv4.ip_forward=1
#Mahimahi Issue: it couldn't make enough interfaces
#Solution: increase max of inotify
sudo sysctl -w -q fs.inotify.max_user_watches=524288
sudo sysctl -w -q fs.inotify.max_user_instances=524288

