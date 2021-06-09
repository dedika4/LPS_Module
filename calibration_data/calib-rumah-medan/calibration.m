dis = [0.5:0.5:5];
t = 30:30:300;
for i=1:7
    plot(t,cal(:,i));
    hold all;
end
title('Plot RSSI Value at Different Distances');
xlabel('Time (second)');
ylabel('Power (dBm)');

