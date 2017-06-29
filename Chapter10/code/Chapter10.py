'''
#The ts object
'''

data (JohnsonJohnson)
class (JohnsonJohnson)
 
frequency (JohnsonJohnson)
 
 

osvisit <- read.csv ( "osvisit.dat" , header= FALSE)
	
osv <- ts (osvisit$V1, start = 1977 , frequency = 12 )
class (osv)

window (osv, start= c ( 1977 , 1 ), end= c ( 1980 , 12 ))


'''
#Visualizing time series data
'''

plot.ts (osv, main="New Zealand Overseas Visitors",ylab="Frequency")


mt <- 1 : 12
names (mt) <- month.name
windows ( height= 20 , width= 30 )
plot (mt,osv[ 1 : 12 ], "l" , col= 1 , ylim= range (osv), ylab= "Overseas Visitors" , xlim= c ( 0 , 13 ))
for(i in 2 : 19 ) points (mt,osv[mt+(i -1 )* 12 ], "l" , col= i)
legend ( x= 4, y= 190000 , legend= c ( 1977 : 1982 ), lty= 1 : 6,
col= 1 : 6 )
legend ( x= 6, y= 190000 , legend= c ( 1983 : 1988 ), lty= 7 : 12,
col= 7 : 12 )
legend ( x= 8, y= 190000 , legend= c ( 1989 : 1995 ), lty= 13 : 19,
col= 13 : 19 )
points (mt,osv[mt+(i -1 )* 12 ], pch= month.abb)
 
 
osv_stl <- stl (osv, s.window= 12 )
plot.ts (osv_stl$time.series)
 
 
'''
#Simple linear regression models
'''

osv_time <- 1 : length (osv)
osv_mths <- as.factor ( rep (month.abb, times= 19 ))
 
 
osv_time <- 1 : length (osv)
osv_mths <- as.factor ( rep (month.abb, times= 19 ))
 
 
osv_season <- lm(osv~osv_mths)
summary(osv_season)
 
 
osv_trend_season <- lm(osv~osv_time+osv_mths)
summary(osv_trend_season)
 
 
windows ( height = 24 , width= 20 )
par ( mfrow= c ( 3 , 1 ))
hist ( residuals (osv_trend), main = "Trend Error" )
hist ( residuals (osv_season), main= "Season Error" )
hist ( residuals (osv_trend_season), main= "Trend+Season Error" )
 
 
 
'''
#ACF and PACF
'''


set.seed ( 12345 )

y <- rnorm ( 500 )
rwy <- cumsum (y)
 
windows ( height= 24 , width= 8 )
par ( mfrow= c ( 3 , 1 ))
plot.ts (rwy, main= "Random Walk" )
acf (rwy, lag.max= 100 , main= "ACF of Random Walk" )
pacf (rwy, main= "PACF of Random Walk" )
 
 
 
'''
#ACF and PACF
'''


set.seed ( 123 )
 t1 <- arima.sim ( list ( order = c ( 1 , 0 , 0 ), ar = 0.6 ), n = 100 )
 t2 <- arima.sim ( list ( order = c ( 0 , 0 , 1 ), ma = - 0.2 ), n = 100 )
 t3 <- arima.sim ( list ( order = c ( 1 , 0 , 1 ), ar = 0.6, ma= - 0.2 ), n = 100 )
 tail (t1); tail (t2); tail (t3)


windows ( height= 30 , width= 20 )
 par ( mfrow= c ( 3 , 2 ))
 acf (t1); pacf (t1)
 acf (t2); pacf (t2)
 acf (t3); pacf (t3)


arima.sim ( list ( order = c ( 1 , 0 , 0 ), ar = 1.6 ), n = 100 ) arima.sim ( list ( order = c ( 0 , 0 , 1 ), ma = 10.2 ), n = 100 )


windows ( height= 10 , width= 20 )
 par ( mfrow= c ( 1 , 2 ))
 acf (osv)
 pacf (osv)


osv_ar <- ar (osv)
 osv_ar


windows ( height= 10 , width= 20 )
 par ( mfrow= c ( 1 , 2 ))
 hist ( na.omit (osv_ar$resid), main= "Histogram of AR Residuals" )
 acf ( na.omit (osv_ar$resid), main= "ACF of AR Residuals" )


auto_ma_order <- function(x,q){
 aicc <- NULL
 for(i in 1 :q) {
 tmodel <- arima (x, order= c ( 0 , 0 ,i))
 aicc[i] <- as.numeric (tmodel$aic)
 }
 return ( which.min (aicc))
 }
 auto_ma_order (osv, 15 )


sapply ( 1 : 20 ,auto_ma_order, x= osv)


# ARIMA Model Fitting
 osv_arima_1 <- arima (osv, order= c ( 1 , 0 , 1 ))
 osv_arima_2 <- arima (osv, order= c ( 2 , 0 , 1 ))
 osv_arima_3 <- arima (osv, order= c ( 1 , 0 , 2 ))
 osv_arima_4 <- arima (osv, order= c ( 1 , 1 , 1 ))
 osv_arima_5 <- arima (osv, order= c ( 2 , 1 , 1 ))
 osv_arima_6 <- arima (osv, order= c ( 1 , 1 , 2 ))
 osv_arima_1; osv_arima_2; osv_arima_3


osv_arima_4; osv_arima_5; osv_arima_6 
 
 
'''
#Accuracy measurements
'''


mean ( residuals (osv_arima_1)) # Mean Error

sqrt ( mean ( residuals (osv_arima_1)^ 2 )) # Root Mean Square Error

mean ( abs ( residuals (osv_arima_1))) # Mean Absolute Error

mean ( residuals (osv_arima_1)/osv)* 100 # Mean Percentage Error

mean ( abs ( residuals (osv_arima_1)/osv))* 100 # Mean Absolute Percentage Error



'''
#Fitting seasonal ARIMA models
'''


osv_seasonal_arima2 <- arima (osv, order= c ( 1 , 1 , 0 ), seasonal= c ( 0 , 1 , 0 ))
 osv_seasonal_arima3 <- arima (osv, order= c ( 1 , 1 , 0 ), seasonal= c ( 1 , 1 , 0 ))
 osv_seasonal_arima4 <- arima (osv, order= c ( 0 , 1 , 1 ), seasonal= c ( 0 , 1 , 1 ))
 osv_seasonal_arima5 <- arima (osv, order= c ( 1 , 1 , 0 ), seasonal= c ( 0 , 1 , 1 ))
 osv_seasonal_arima6 <- arima (osv, order= c ( 0 , 1 , 1 ), seasonal= c ( 1 , 1 , 0 ))
 osv_seasonal_arima7 <- arima (osv, order= c ( 1 , 1 , 1 ), seasonal= c ( 1 , 1 , 1 ))
 osv_seasonal_arima8 <- arima (osv, order= c ( 1 , 1 , 1 ), seasonal= c ( 1 , 1 , 0 ))
 osv_seasonal_arima9 <- arima (osv, order= c ( 1 , 1 , 1 ), seasonal= c ( 0 , 1 , 1 ))
 
 
 accuracy (osv_seasonal_arima2)[ 5 ]
 
 accuracy (osv_seasonal_arima3)[ 5 ]
 
 accuracy (osv_seasonal_arima4)[ 5 ]
 
 accuracy (osv_seasonal_arima5)[ 5 ]

 accuracy (osv_seasonal_arima6)[ 5 ]
 
 accuracy (osv_seasonal_arima7)[ 5 ]
 
 accuracy (osv_seasonal_arima8)[ 5 ]
 
 accuracy (osv_seasonal_arima9)[ 5 ]
 
 
 
 opt_model <- auto.arima (osv, max.p= 6 , max.q= 6 , max.d= 4 , max.P= 3 , max.Q= 3 , max.D= 3 )
opt_model


accuracy (opt_model)
