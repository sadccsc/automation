p=anom
screen -dmS "session1$p" sh -c "./calc_etccdi.sh 19810101 19891231 ; exec bash"
screen -dmS "session2$p" sh -c "./calc_etccdi.sh 19900101 19991231 ; exec bash"
screen -dmS "session3$p" sh -c "./calc_etccdi.sh 20000101 20091231 ; exec bash"
screen -dmS "session4$p" sh -c "./calc_etccdi.sh 20100101 20191231 ; exec bash"
screen -dmS "session5$p" sh -c "./calc_etccdi.sh 20200101 20231231 ; exec bash"

