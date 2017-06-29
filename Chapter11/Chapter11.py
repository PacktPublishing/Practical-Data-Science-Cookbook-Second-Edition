'''
#Simple data transformations
'''

library (data.table)
library (dplyr)
library (RSADBE)
library (rpart)
library (randomForestSRC)
library (ROCR)
library (plyr)

data (GC)
 GC2 <- GC
 GC2$checking <- as.factor (GC2$checking)
 GC2$checking <- revalue (GC2$checking, c ( "1" = "< 0 DM" , "2" = "0 <= ... < 200 DM" ,
 "3" = ">= 200 DM" , "4" = "No Acc" ))
 
''' 
# Visualizing categorical data
 '''
 barplot ( table (GC2$good_bad))
 
 table (GC2$good_bad,GC2$housing)
 prop.table ( table (GC2$good_bad,GC2$housing),margin= 2 )
 
 prop.table ( table (GC2$good_bad,GC2$employed),margin= 2 )
 prop.table ( table (GC2$good_bad,GC2$checking),margin= 2 )
 
 
 
 windows ( height= 15 , width= 10 )
 par ( mfrow= c ( 3 , 1 ))
 mosaicplot (~good_bad+housing,GC2)
 mosaicplot (~good_bad+employed,GC2)
 mosaicplot (~good_bad+checking,GC2)
 
 '''
 #Discriminant analysis
 '''
 data (iris)
 str (iris)
 
 
 summary (iris)
 
 
 iris_lda <- lda (Species~.,iris)
 iris_lda

 
 
 iris_lda_values <- predict (iris_lda)
 windows ( height= 20 , width= 10 )
 ldahist (iris_lda_values$x[, 1 ], g= iris$Species)
 
 table ( predict (iris_lda)$class)
 table (iris$Species, predict (iris_lda)$class)
 
 GB_lda <- lda (good_bad~.,GC2)
 GB_lda

 table ( predict (GB_lda)$class)
 table (GC2$good_bad, predict (GB_lda)$class)
 
 '''
 Dividing the data and the ROC
 '''
 
 set.seed ( 1234567 )
 
 data_part_label <- c ( "Train" , "Validate" , "Test" )
 
 indv_label = sample (data_part_label, size= 1000 , replace= TRUE ,prob
 = c ( 0.6 , 0.2 , 0.2 ))
 GC_Train <- GC2[indv_label== "Train" ,]
 GC_Validate <- GC2[indv_label== "Validate" ,]
 GC_Test <- GC2[indv_label== "Test" ,]
 
 example(performance)
 
 
 '''
# Fitting the logistic regression model
 '''
 
 GC_Logistic <- glm (good_bad~., data= GC_Train, family= 'binomial' )
summary (GC_Logistic)


table (GC_Train$good_bad)

table (GC_Train$good_bad, ifelse ( predict (GC_Logistic, type= "response" )> 0.5 , "good" , "bad" ))

'''
#Decision trees and rules
'''

library (rpart)
 data (kyphosis)
 
 kyphosis_rpart <- rpart (Kyphosis~.,kyphosis)
 plot (kyphosis_rpart, uniform= TRUE )
 text (kyphosis_rpart)
 
 asRules (kyphosis_rpart)
 
 kyphosis$where <- kyphosis_rpart$where
 table (kyphosis$Kyphosis,kyphosis$where)

 
 K2 <- data.table (kyphosis)
 K2[, prop.table ( table (Kyphosis))]

 
 K2[Start>= 12.5 , prop.table ( table (Kyphosis))]
 K2[Start < 12.5 & Age <= 35 , prop.table ( table (Kyphosis))]
 K2[Start < 12.5 & Age > 35 & Number < 4.5 , prop.table ( table (Kyphosis))]
 K2[Start < 12.5 & Age > 35 & Number >= 4.5 , prop.table ( table (Kyphosis))]
 
 '''
 #Decision tree for german data
 '''
 
 GC_CT <- rpart (good_bad~., data= GC_Train)
 windows ( height= 20 , width= 20 )
 plot (GC_CT, uniform = TRUE ); text (GC_CT)
 
 table (GC_Train$good_bad, predict (GC_CT, type= "class" ))
 GC_CT$cptable
  GC_CT$variable.importance
  
  GC_CT_Train_Prob <- predict (GC_CT, newdata= GC_Train[,- 21 ], type= "prob" )[, 2 ]
 GC_CT_Validate_Prob <- predict (GC_CT, newdata= GC_Validate[,- 21 ], type= "prob" )[, 2 ]
 GB_CT_Train_roc <- roc (GC_Train$good_bad,GC_CT_Train_Prob)
 GB_CT_Validate_roc <- roc (GC_Validate$good_bad,GC_CT_Validate_Prob) roc.test (GB_Logistic_Train_roc,GB_CT_Train_roc)
 roc.test (GB_Logistic_Validate_roc,GB_CT_Validate_roc)	