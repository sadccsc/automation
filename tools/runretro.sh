for year in {1981..2021}; do
for month in {01..12};do
./calc_seasaccum.sh ${year}0601 ${year}0331
done
done
