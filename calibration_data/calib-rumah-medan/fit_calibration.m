function createfigure(X1, Y1)
%CREATEFIGURE(X1, Y1)
%  X1:  vector of x data
%  Y1:  vector of y data

%  Auto-generated by MATLAB on 10-May-2021 09:17:38

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot1 = plot(X1,Y1,'DisplayName','data1','Parent',axes1,'Marker','*',...
    'LineWidth',1,...
    'Color',[0 0.447058823529412 0.741176470588235]);

% Get xdata from plot
xdata1 = get(plot1, 'xdata');
% Get ydata from plot
ydata1 = get(plot1, 'ydata');
% Make sure data are column vectors
xdata1 = xdata1(:);
ydata1 = ydata1(:);


% Remove NaN values and warn
nanMask1 = isnan(xdata1(:)) | isnan(ydata1(:));
if any(nanMask1)
    warning('GeneratedCode:IgnoringNaNs', ...
        'Data points with NaN coordinates will be ignored.');
    xdata1(nanMask1) = [];
    ydata1(nanMask1) = [];
end

% Find x values for plotting the fit based on xlim
axesLimits1 = xlim(axes1);
xplot1 = linspace(axesLimits1(1), axesLimits1(2));

% Prepare for plotting residuals
set(axes1,'position',[0.1300    0.5811    0.7750    0.3439]);
residAxes1 = axes('position', [0.1300    0.1100    0.7750    0.3439], ...
    'parent', gcf);
savedResids1 = zeros(length(xdata1), 1);
% Sort residuals
[sortedXdata1, xInd1] = sort(xdata1);

% Preallocate for "Show equations" coefficients
coeffs1 = cell(1,1);

% Find coefficients for polynomial (order = 5)
[fitResults1,~,mu1] = polyfit(xdata1,ydata1,5);
% Evaluate polynomial
yplot1 = polyval(fitResults1,xplot1,[],mu1);

% Save type of fit for "Show norm of residuals" and "Show equations"
fittypesArray1(1) = 6;

% Calculate and save residuals - evaluate using original xdata
Yfit1 = polyval(fitResults1,xdata1,[],mu1);
resid1 = ydata1 - Yfit1(:);
savedResids1(:,1) = resid1(xInd1);
savedNormResids1(1) = norm(resid1);

% Save coefficients for "Show Equation"
coeffs1{1} = fitResults1;

% Plot the fit
fitLine1 = plot(xplot1,yplot1,'DisplayName','   5th degree',...
    'Tag','5th degree',...
    'Parent',axes1,...
    'Color',[0.635 0.078 0.184]);

% Set new line in proper position
setLineOrder(axes1,fitLine1,plot1);

% Plot residuals in a bar plot
residPlot1 = bar(residAxes1, sortedXdata1, savedResids1);
% Set colors to match fit lines
set(residPlot1(1), 'facecolor', [0.635 0.078 0.184],'edgecolor', [0.635 0.078 0.184]);
% Set residual plot axis title
title(residAxes1, 'residuals');

% "Show norm of residuals" was selected
showNormOfResiduals(residAxes1,fittypesArray1,savedNormResids1);

% "Show equations" was selected
showEquations(fittypesArray1,coeffs1,4,axes1,xdata1);

% Create ylabel
ylabel('Mean RSSI (dBm)');

% Create xlabel
xlabel('Log Distance');

% Create title
title('Plot RSSI vs Distance');

% Uncomment the following line to preserve the X-limits of the axes
% xlim(axes1,[-0.4 0.8]);
box(axes1,'on');
grid(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'OuterPosition',[0 0.5 1 0.5]);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,'Visible','off');

%-------------------------------------------------------------------------%
function setLineOrder(axesh1, newLine1, associatedLine1)
%SETLINEORDER(AXESH1,NEWLINE1,ASSOCIATEDLINE1)
%  Set line order
%  AXESH1:  axes
%  NEWLINE1:  new line
%  ASSOCIATEDLINE1:  associated line

% Get the axes children
hChildren = get(axesh1,'Children');
% Remove the new line
hChildren(hChildren==newLine1) = [];
% Get the index to the associatedLine
lineIndex = find(hChildren==associatedLine1);
% Reorder lines so the new line appears with associated data
hNewChildren = [hChildren(1:lineIndex-1);newLine1;hChildren(lineIndex:end)];
% Set the children:
set(axesh1,'Children',hNewChildren);

%-------------------------------------------------------------------------%
function showNormOfResiduals(residaxes1, fittypes1, normResids1)
%SHOWNORMOFRESIDUALS(RESIDAXES1,FITTYPES1,NORMRESIDS1)
%  Show norm of residuals
%  RESIDAXES1:  axes for residuals
%  FITTYPES1:  types of fits
%  NORMRESIDS1:  norm of residuals

txt = cell(length(fittypes1) ,1);
for i = 1:length(fittypes1)
    txt{i,:} = getResidString(fittypes1(i),normResids1(i));
end
% Save current axis units; then set to normalized
axesunits = get(residaxes1,'units');
set(residaxes1,'units','normalized');
text(.05,.95,txt,'parent',residaxes1, ...
    'verticalalignment','top','units','normalized');
% Reset units
set(residaxes1,'units',axesunits);

%-------------------------------------------------------------------------%
function [s1] = getResidString(fittype1, normResid1)
%GETRESIDSTRING(FITTYPE1,NORMRESID1)
%  Get "Show norm of residuals" text
%  FITTYPE1:  type of fit
%  NORMRESID1:  norm of residuals

% Get the text from the message catalog.
switch fittype1
    case 0
        s1 = getString(message('MATLAB:graph2d:bfit:ResidualDisplaySplineNorm'));
    case 1
        s1 = getString(message('MATLAB:graph2d:bfit:ResidualDisplayShapepreservingNorm'));
    case 2
        s1 = getString(message('MATLAB:graph2d:bfit:ResidualDisplayLinearNorm', num2str(normResid1)));
    case 3
        s1 = getString(message('MATLAB:graph2d:bfit:ResidualDisplayQuadraticNorm', num2str(normResid1)));
    case 4
        s1 = getString(message('MATLAB:graph2d:bfit:ResidualDisplayCubicNorm', num2str(normResid1)));
    otherwise
        s1 = getString(message('MATLAB:graph2d:bfit:ResidualDisplayNthDegreeNorm', fittype1-1, num2str(normResid1)));
end

%-------------------------------------------------------------------------%
function showEquations(fittypes1, coeffs1, digits1, axesh1, xdata1)
%SHOWEQUATIONS(FITTYPES1,COEFFS1,DIGITS1,AXESH1,XDATA1)
%  Show equations
%  FITTYPES1:  types of fits
%  COEFFS1:  coefficients
%  DIGITS1:  number of significant digits
%  AXESH1:  axes
%  XDATA1:  x data

n = length(fittypes1);
txt = cell(length(n + 2) ,1);
txt{1,:} = ' ';
for i = 1:n
    txt{i + 1,:} = getEquationString(fittypes1(i),coeffs1{i},digits1,axesh1);
end
meanx = mean(xdata1);
stdx = std(xdata1);
format = ['where z = (x - %0.', num2str(digits1), 'g)/%0.', num2str(digits1), 'g'];
txt{n + 2,:} = sprintf(format, meanx, stdx);
text(.05,.95,txt,'parent',axesh1, ...
    'verticalalignment','top','units','normalized');

%-------------------------------------------------------------------------%
function [s1, a1] = getEquationString(fittype1, coeffs1, digits1, axesh1)
%GETEQUATIONSTRING(FITTYPE1,COEFFS1,DIGITS1,AXESH1)
%  Get "Show Equation" text
%  FITTYPE1:  type of fit
%  COEFFS1:  coefficients
%  DIGITS1:  number of significant digits
%  AXESH1:  axes

if isequal(fittype1, 0)
    s1 = 'Cubic spline interpolant';
elseif isequal(fittype1, 1)
    s1 = 'Shape-preserving interpolant';
else
    if isequal(fittype1, 2)
        a1 = 'Linear: ';
    elseif isequal(fittype1, 3)
        a1 = 'Quadratic: ';
    elseif isequal(fittype1, 4)
        a1 = 'Cubic: ';
    elseif isequal(fittype1, 5)
        a1 = '4th degree: ';
    elseif isequal(fittype1, 6)
        a1 = '5th degree: ';
    elseif isequal(fittype1, 7)
        a1 = '6th degree: ';
    elseif isequal(fittype1, 8)
        a1 = '7th degree: ';
    elseif isequal(fittype1, 9)
        a1 = '8th degree: ';
    elseif isequal(fittype1, 10)
        a1 = '9th degree: ';
    elseif isequal(fittype1, 11)
        a1 = '10th degree: ';
    end
    op = '+-';
    format1 = ['%s %0.',num2str(digits1),'g*z^{%s} %s'];
    format2 = ['%s %0.',num2str(digits1),'g'];
    xl = get(axesh1, 'xlim');
    fit =  fittype1 - 1;
    s1 = sprintf('%s y =',a1);
    th = text(xl*[.95;.05],1,s1,'parent',axesh1, 'vis','off');
    if abs(coeffs1(1) < 0)
        s1 = [s1 ' -'];
    end
    for i = 1:fit
        sl = length(s1);
        if ~isequal(coeffs1(i),0) % if exactly zero, skip it
            s1 = sprintf(format1,s1,abs(coeffs1(i)),num2str(fit+1-i), op((coeffs1(i+1)<0)+1));
        end
        if (i==fit) && ~isequal(coeffs1(i),0)
            s1(end-5:end-2) = []; % change x^1 to x.
        end
        set(th,'string',s1);
        et = get(th,'extent');
        if et(1)+et(3) > xl(2)
            s1 = [s1(1:sl) sprintf('\n     ') s1(sl+1:end)];
        end
    end
    if ~isequal(coeffs1(fit+1),0)
        sl = length(s1);
        s1 = sprintf(format2,s1,abs(coeffs1(fit+1)));
        set(th,'string',s1);
        et = get(th,'extent');
        if et(1)+et(3) > xl(2)
            s1 = [s1(1:sl) sprintf('\n     ') s1(sl+1:end)];
        end
    end
    delete(th);
    % Delete last "+"
    if isequal(s1(end),'+')
        s1(end-1:end) = []; % There is always a space before the +.
    end
    if length(s1) == 3
        s1 = sprintf(format2,s1,0);
    end
end

