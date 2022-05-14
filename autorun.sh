while true; do
	cd /home/dev/new
 	python3 ble_connect_multiprocessing.py
	echo "# Error happened during the code execution!"
	sleep 5
	sudo killall python &>/dev/null	
	sudo killall python3 &>/dev/null
	sleep 5
done
