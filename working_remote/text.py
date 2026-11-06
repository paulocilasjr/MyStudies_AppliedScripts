squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release

scontrol update JobId=21774339 ArrayTaskThrottle=8

squeue -u "$USER" -t R -o "%.18i %.24j %.11M %R"
