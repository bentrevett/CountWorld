b=(32 64 126 256)
c=(0.1 1 10 100)
ed=(16 32 64 128 256)
sed=(32 64 128 256 512)
qd=(32 64 128 256 512)
std=(32 64 128 256 512)
do=(0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9)

while true
do
    rb=$[$RANDOM % ${#b[@]}]
    rc=$[$RANDOM % ${#c[@]}]
    red=$[$RANDOM % ${#ed[@]}]
    rsed=$[$RANDOM % ${#sed[@]}]
    rqd=$[$RANDOM % ${#qd[@]}]
    rstd=$[$RANDOM % ${#std[@]}]
    rdo=$[$RANDOM % ${#do[@]}]

    python lstm_run.py --batch_size ${b[$rb]} --clip ${c[$rc]} --emb_dim ${ed[$red]} --sent_hid_dim ${sed[$rsed]} --query_hid_dim ${qd[$rqd]} --story_hid_dim ${std[$rstd]} --dropout ${do[$rdo]}
done