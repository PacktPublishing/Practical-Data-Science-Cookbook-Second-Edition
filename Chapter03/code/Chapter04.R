#Install and load packages necessary for this chapter

install.packages("XML")
install.packages("ggplot2")
install.packages("plyr")
install.packages("reshape2")
install.packages("zoo")

library(XML)
library(ggplot2)
library(plyr)
library(reshape2)
library(zoo)

setwd("path/where/you/want/to save/charts")

#Read the finviz.csv file
finviz <- read.csv("path/finviz.csv")

#Or to pull finviz stock screener data straight from the web...
#Get the URL string
url_to_open <- 'http://finviz.com/export.ashx?v=152&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68'

#Or to avoid having to type all the numbers from 0-68...
url_to_open <- sprintf("http://finviz.com/export.ashx?v=152&c=%s",  paste(0:68, collapse = ","))

#Read the data from the csv file into a data frame
finviz <- read.csv(url(url_to_open))


#Clean up the data
#Create a function listing the special characters you want to remove individually
clean_numeric <- function(s){
  s <- gsub("%|\\$|,|\\)|\\(", "", s)
  s <- as.numeric(s)
}

finviz <- cbind(finviz[,1:6],apply(finviz[,7:68], 2, clean_numeric))

#Explore the data
hist(finviz$Price, breaks=100, main="Price Distribution", xlab="Price")
hist(finviz$Price[finviz$Price<150], breaks=100, main="Price Distribution", xlab="Price")

sector_avg_prices <- aggregate(Price~Sector,data=finviz,FUN="mean")
colnames(sector_avg_prices)[2] <- "Sector_Avg_Price"

ggplot(sector_avg_prices, aes(x=Sector, y=Sector_Avg_Price, fill=Sector)) + 
  geom_bar(stat="identity") + ggtitle("Sector Avg Prices") + 
  theme(axis.text.x = element_text(angle = 90, hjust = 1))


industry_avg_prices <- aggregate(Price~Sector+Industry,data=finviz,FUN="mean")
industry_avg_prices <- industry_avg_prices[order(industry_avg_prices$Sector,industry_avg_prices$Industry),]
colnames(industry_avg_prices)[3] <- "Industry_Avg_Price"

industry_chart <- subset(industry_avg_prices,Sector=="Financial")

ggplot(industry_chart, aes(x=Industry, y=Industry_Avg_Price, fill=Industry)) + 
  geom_bar(stat="identity") + theme(legend.position="none") + ggtitle("Industry Avg Prices") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

company_chart <- subset(finviz,Industry=="Property & Casualty Insurance")

ggplot(company_chart, aes(x=Company, y=Price, fill=Company)) + 
  geom_bar(stat="identity") + theme(legend.position="none") + 
  ggtitle("Company Avg Prices") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

finviz <- subset(finviz, Ticker!="BRK-A")

#Add sector and industry averages to finviz data frame
sector_avg <- melt(finviz, id="Sector")
sector_avg <- subset(sector_avg,variable%in%c("Price","P.E","PEG","P.S","P.B"))

sector_avg <- (na.omit(sector_avg))
sector_avg$value <- as.numeric(sector_avg$value)

sector_avg <- dcast(sector_avg, Sector~variable, mean)
colnames(sector_avg)[2:6] <- c("SAvgPE","SAvgPEG","SAvgPS","SAvgPB","SAvgPrice") 

industry_avg <- melt(finviz, id=c("Sector","Industry"))
industry_avg <- subset(industry_avg,variable %in% c("Price","P.E","PEG","P.S","P.B"))
industry_avg <- (na.omit(industry_avg))
industry_avg$value <- as.numeric(industry_avg$value)
industry_avg <- dcast(industry_avg, Sector+Industry~variable, mean)
industry_avg <- (na.omit(industry_avg))
colnames(industry_avg)[3:7] <- c("IAvgPE","IAvgPEG","IAvgPS","IAvgPB","IAvgPrice") 

finviz <- merge(finviz, sector_avg, by.x="Sector", by.y="Sector")
finviz <- merge(finviz, industry_avg, by.x=c("Sector","Industry"), by.y=c("Sector","Industry"))

#Create undervalued columns and give them a 1 or 0.  
finviz$SPEUnder <- 0
finviz$SPEGUnder <- 0
finviz$SPSUnder <- 0
finviz$SPBUnder <- 0
finviz$SPriceUnder <- 0
finviz$IPEUnder <- 0
finviz$IPEGUnder <- 0
finviz$IPSUnder <- 0
finviz$IPBUnder <- 0
finviz$IPriceUnder <- 0

finviz$SPEUnder[finviz$P.E<finviz$SAvgPE] <- 1
finviz$SPEGUnder[finviz$PEG<finviz$SAvgPEG] <- 1
finviz$SPSUnder[finviz$P.S<finviz$SAvgPS] <- 1
finviz$SPBUnder[finviz$P.B<finviz$SAvgPB] <- 1
finviz$SPriceUnder[finviz$Price<finviz$SAvgPrice] <- 1
finviz$IPEUnder[finviz$P.E<finviz$IAvgPE] <- 1
finviz$IPEGUnder[finviz$PEG<finviz$IAvgPEG] <- 1
finviz$IPSUnder[finviz$P.S<finviz$IAvgPS] <- 1
finviz$IPBUnder[finviz$P.B<finviz$IAvgPB] <- 1
finviz$IPriceUnder[finviz$Price<finviz$IAvgPrice] <- 1

finviz$RelValIndex <- apply(finviz[79:88],1,sum)

potentially_undervalued <- subset(finviz,RelValIndex>=8)[,c(4,5,89)]


#Filter the list down to your target stocks
target_stocks <- subset(finviz, Price>20 & Price<100 & Volume>10000 & 
                          Country=="USA" &  
                          EPS..ttm.>0 & 
                          EPS.growth.next.year>0 & 
                          EPS.growth.next.5.years>0 & 
                          Total.Debt.Equity<1 & Beta<1.5 & 
                          Institutional.Ownership<30 & 
                          RelValIndex>8)


#Pull historical prices
counter <- 0

for (symbol in target_stocks$Ticker){
  
  url <- paste0("http://ichart.finance.yahoo.com/table.csv?s=",symbol,"&a=08&b=7&c=1984&d=01&e=23&f=2014&g=d&ignore=.csv")
  
  stock <- read.csv(url)
  stock <- na.omit(stock)
  colnames(stock)[7] <- "AdjClose"
  stock[,1] <- as.Date(stock[,1])
  stock <- cbind(Symbol=symbol,stock)
  
  maxrow <- nrow(stock)-49
  ma50 <- cbind(stock[1:maxrow,1:2],rollmean(stock$AdjClose,50,align="right"))
  maxrow <- nrow(stock)-199
  ma200 <- cbind(stock[1:maxrow,1:2],rollmean(stock$AdjClose,200,align="right"))
  
  stock <- merge(stock,ma50,by.x=c("Symbol","Date"),by.y=c("Symbol","Date"),all.x=TRUE)
  colnames(stock)[9] <- "MovAvg50"  
  stock <- merge(stock,ma200,by.x=c("Symbol","Date"),by.y=c("Symbol","Date"),all.x=TRUE)
  colnames(stock)[10] <- "MovAvg200"
  
  price_chart <- melt(stock[,c(1,2,8,9,10)],id=c("Symbol","Date"))
  
  qplot(Date, value, data=price_chart, geom="line", color=variable,
        main=paste(symbol,"Daily Stock Prices"),ylab="Price")
  ggsave(filename=paste0("stock_price_",counter,".png"))
  
  price_summary <- ddply(stock, "Symbol", summarise, open=Open[nrow(stock)],
                         high=max(High),low=min(Low),close=AdjClose[1])
    
  #Compile prices and summaries for all symbols into a single data frame
  if(counter==0){
    stocks <- rbind(stock)
    price_summaries <- rbind(price_summary)
  }else{
    stocks <- rbind(stocks, stock)
    price_summaries <- rbind(price_summaries, price_summary)
  }
  counter <- counter+1
}

#Plot prices over time for each symbol
qplot(Date, AdjClose, data=stocks, geom="line", color=Symbol,
      main="Daily Stock Prices")
ggsave(filename=("stock_price_combined.png"))


#Create bar graph showing the summaries for each stock
summary <- melt(price_summaries,id="Symbol")

ggplot(summary, aes(x=variable, y=value, fill=Symbol)) +  
  geom_bar(stat="identity") + facet_wrap(~Symbol) + theme(legend.position="none")
ggsave(filename=("stock_price_summaries.png"))


