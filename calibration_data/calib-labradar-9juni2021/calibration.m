%% Data Integration %%
original_data = [powerat1m powerat2m powerat3m powerat4m powerat5m powerat6m powerat7m powerat8m powerat9m powerat10m powerat11m powerat12m powerat13m];

%% Save To File %%
writematrix(original_data,'original_data.csv');

%% Plot Raw %%
dis = [1:1:13];
t = 20:10:180;
for i=1:13
    plot(t,original_data(:,i));
    hold all;
end
title('Plot RSSI Value at Different Distances vs Time');
xlabel('Time (second)');
ylabel('Power (dBm)');

%% Calculate Average %%
avg = sum(original_data)/17;
log_dis = log10(dis);

plot(log_dis,avg);
title('Mean RSSI Value vs Log Distance');
xlabel('Log Distance');
ylabel('Mean Power (dBm)');

editted_dis = [1 3:10];
log_editted_dis = log10(editted_dis);
editted_avg = [avg(1) avg(3:10)];

plot(log_editted_dis,editted_avg);
title('Mean RSSI Value vs Log Distance');
xlabel('Log Distance');
ylabel('Mean Power (dBm)');