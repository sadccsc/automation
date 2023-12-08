#!/bin/bash

ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
#
# sample input file:
#
if [[ ! -f ${ABSDIR}/functions ]]; then
  echo "functions script not found. exit..."
  exit
fi
source ${ABSDIR}/iniEnv
source ${ABSDIR}/functions
source ${ABSDIR}/bin/activate

cdate=$1
if [[ -z $cdate ]]; then
    cdate=$(date -I)
fi

yesterday=$(date +%Y%m%d -d "$cdate - 1 day")
year=$(date -d $cdate +%Y)
cmonth=$(date -d $cdate +%Y%m)
day=$(date -d $cdate +%d)
lmonth=$(date +%Y%m -d "$cdate - 1 month")
pmonth=${lmonth}01
echo day $day
echo cmonth $cmonth
echo lmonth $lmonth
echo pmonth $pmonth
#exit
#
case "$day" in
  0[1-5])
    pentads=$(echo ${lmonth}{01,06,11,16,21,26})
	dekads=$(echo ${lmonth}{01,11,21})
	echo 01-05
	;;
  0[6-9]|10)
    pentads=$(echo ${lmonth}{06,11,16,21,26} ${cmonth}01)
	dekads=$(echo ${lmonth}{01,11,21})
	echo 06-10
	;;
  1[1-5])
    pentads=$(echo ${lmonth}{11,16,21,26} ${cmonth}{01,06})
	dekads=$(echo ${lmonth}{11,21} ${cmonth}01)
	echo 11-15
	;;
  1[6-9]|20)
    pentads=$(echo ${lmonth}{16,21,26} ${cmonth}{01,06,11})
	dekads=$(echo ${lmonth}{11,21} ${cmonth}01)
	echo 16-20
	;;
  2[1-5])
    pentads=$(echo ${lmonth}{21,26} ${cmonth}{01,06,11,16})
	dekads=$(echo ${lmonth}21 ${cmonth}{01,11})
	echo 21-25
	;;
  2[6-9]|3*)
    pentads=$(echo ${lmonth}26 ${cmonth}{01,06,11,16,21})
	dekads=$(echo ${lmonth}21 ${cmonth}{01,11})
	echo 26-31
	;;
esac

cdate=20230118

freq="daily"
echo -e "\n"
echo mysql -N -h ${sqlhost} -u ${sqluser} -p${sqlpass} -D ${sqldb} -e "select id from metadata where freq='$freq';"
mysql -N -h ${sqlhost} -u ${sqluser} -p${sqlpass} -D ${sqldb} -e "select id from metadata where freq='$freq';" | while read prod; do
 echo
 echo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 echo $prod
 python $ABSDIR/csc-quicklooks.py ${prod} ${cdate}
 #exit
done

exit

