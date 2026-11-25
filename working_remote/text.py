"${rx_cmd[@]}" submit E13 && qstat

"${rx_cmd[@]}" status E13

less "$RX_ROOT/E13/results/report.md"
