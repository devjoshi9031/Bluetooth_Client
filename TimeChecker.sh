#!/bin/bash
run_once_flag=1
now=`date`
DC_CNT=1
MAX_RETRIES=5
sleep 3
sudo ifconfig wlan0 up

while true; do
        wget --spider --quiet --read-timeout=2 --tries=3 http://google.com
        if [ "$?" != 0 ]; then
                echo "[Time: $now] # Error!!! Check the internet connection! Retry Number $DC_CNT"
                ssidName=$(/usr/sbin/iwgetid -r)
                if [ -z "$ssidName" ]
                then
                          echo "[Time: $now] WiFi is not connected!"
                else
                        echo "[Time: $now] #WiFi is connected to $ssidName"
                fi

                DC_CNT=$((DC_CNT+1))

                if [ $DC_CNT -gt $MAX_RETRIES ]
                then
                        echo "[Time: $now] # Connection was unsuccessful for $MAX_RETRIES times. Restarting the WiFi... "
                        sudo ifconfig wlan0 down
                        sleep 15
                        echo "[Time: $now] #WiFi is down"
                        sleep 15
                        sudo ifconfig wlan0 up
                        sleep 70
                        DC_CNT=0
                        echo "[Time: $now] #WiFi is up again"
                        ssidName=$(/usr/sbin/iwgetid -r)
                        if [ -z "$ssidName" ]
                        then
                                echo "[Time: $now] WiFi is not connected!"
                        else
                                echo "[Time: $now] #WiFi is connected to $ssidName"
                        fi

                fi
        else
                DC_CNT=0
                ssidName=$(/usr/sbin/iwgetid -r)
                if [ -z "$ssidName" ]
                then
                        echo "[Time: $now] WiFi is not connected!"
                else
                        echo "[Time: $now] #WiFi is connected to $ssidName"
                        if [ $run_once_flag == 1 ]
                        then
                                run_once_flag=0
                                echo "[Time: $now] # Date has been updated successfully!" 
                                sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 \
                                | grep Date: | cut -d' ' -f5-8)Z"
                                now=`date`
                        fi
                        
                                
                fi

        fi
        sleep 5
done




############################# Earlier version of the bash file ##############################
# while true; do
#     wget --spider --quiet --read-timeout=3 --tries=3 http://google.com
#     if [ "$?" != 0 ]; then
#         echo "Time: $now # Error!!! Check the internet connection!"
#                 ssidName=$(/usr/sbin/iwgetid -r)
#                 if [ -z "$ssidName" ]
#                 then
#                         echo "WiFi is not connected!"
#                 else
#                         echo "#WiFi is connected to $ssidName"
#                 fi
#         sleep 5
#     else
#         echo "# Date has been updated successfully!" 
#         sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 \
#                     | grep Date: | cut -d' ' -f5-8)Z"
#             break
#     fi
# done
