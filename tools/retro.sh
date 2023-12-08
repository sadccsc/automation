cdate=$(date -I)

cdate=$(date +%Y%m%d)

d=$(date -d "$cdate - 7 day" +%Y%m%d)

while [ $d -lt $cdate ]; do 
    d=$(date -d "$d + 1 day" +%Y%m%d)
    qdate=$(date -d "$d + 1 day" +%Y-%m-%d)
    ./generate-all-quicklooks.sh $qdate
    ./sync-website.sh $d
done

