#Preparing for analysis
install.packages('data.table')
install.packages('sqldf')
install.packages('dplyr')
install.packages('stringr')
install.packages('ggplot2')
install.packages('maps')
install.packages('bit64')
install.packages('RColorBrewer')
install.packages('choroplethr')
install.packages('rbenchmark')
install.packages('microbenchmark')

library(bit64)
library(data.table)
library(sqldf)
library(plyr)
library(dplyr)
library(stringr)
library(ggplot2)
library(maps)
library(RColorBrewer)
library(choroplethr)
library(rbenchmark)
library(microbenchmark)



#Importing employment data into R
ann2012 <- read.csv(unz('data/2012_annual_singlefile.zip','2012.annual.singlefile.csv'),stringsAsFactors=F)
ann2012 <- read.csv('data/2012.annual.singlefile.csv', stringsAsFactors=F)

#or 
ann2012 <- fread('data/2012.annual.singlefile.csv')


#Exploring the employment data
dim(ann2012)
head(ann2012)

ann2012 <- fread('2012.annual.singlefile.csv', sep=',', colClasses=c('character', 'integer', 'integer', 'integer', 'integer', 'integer', 'character',rep('integer',8)))


#Obtaining and merging additional data
for(u in c('agglevel','area','industry',
           'ownership','size')){
  assign(u,read.csv(paste('data/',u,'_titles.csv',sep=''), stringsAsFactors=F))
}

intersect(names(agglevel),names(ann2012))

codes <- c('agglevel','industry','ownership','size')
ann2012full <- ann2012
for(i in 1:length(codes)){
  eval(parse(text=paste('ann2012full <- left_join(ann2012full, ',codes[i],')', sep='')))
}


#Adding geographical information
head(area)

simpleCap <-function(x){
  if(!is.na(x)){
    s <- strsplit(x,' ')[[1]]
    paste(toupper(substring(s,1,1)), substring(s,2), 
          sep='', collapse=' ')
  } else {NA}
}

data(county.fips)
head(county.fips)

county.fips$fips <- str_pad(county.fips$fips, width=5, pad="0")

county.fips$polyname <- as.character(county.fips$polyname)
county.fips$county <- sapply(
  gsub('[a-z\ ]+,([a-z\ ]+)','\\1',county.fips$polyname),
  simpleCap)
county.fips <- unique(county.fips)

data(state.fips)
head(state.fips)

state.fips$fips <- str_pad(state.fips$fips, width=2, pad="0", side='left')
state.fips$state <- as.character(state.fips$polyname)
state.fips$state <- 
  gsub("([a-z\ ]+):[a-z\ \\']+",'\\1',state.fips$state)
state.fips$state <- sapply(state.fips$state, simpleCap)

mystatefips <-unique(state.fips[,c('fips','abb','state')])

lower48 <- setdiff(unique(state.fips$state),c('Hawaii','Alaska'))

myarea <- merge(area, county.fips, by.x='area_fips',by.y='fips', all.x=T)
myarea$state_fips <- substr(myarea$area_fips, 1,2)
myarea <- merge(myarea, mystatefips,by.x='state_fips',by.y='fips', all.x=T)

ann2012full <- left_join(ann2012full, myarea)
ann2012full <- filter(ann2012full, state %in% lower48)

save(ann2012full, file='data/ann2014full.rda',compress=T)

#Extracting state- and county-level wage and employment information
d.state <- filter(ann2012full, agglvl_code==50)
d.state <- select(d.state, state, avg_annual_pay, annual_avg_emplvl)

d.state$wage <- cut(d.state$avg_annual_pay, quantile(d.state$avg_annual_pay, c(seq(0,.8, by=.2), .9, .95, .99, 1)))
d.state$empquantile <- cut(d.state$annual_avg_emplvl, quantile(d.state$annual_avg_emplvl, c(seq(0,.8,by=.2),.9,.95,.99,1)))

x <- quantile(d.state$avg_annual_pay, c(seq(0,.8,by=.2),.9, .95, .99, 1))
xx <- paste(round(x/1000),'K',sep='')
Labs <- paste(xx[-length(xx)],xx[-1],sep='-')
levels(d.state$wage) <- Labs

x <- quantile(d.state$annual_avg_emplvl, c(seq(0,.8,by=.2),.9, .95, .99, 1))
xx <- ifelse(x>1000, paste(round(x/1000),'K',sep=''),round(x))

Labs <- paste(xx[-length(xx)],xx[-1],sep='-')
levels(d.state$empquantile) <- Labs

Discretize <- function(x, breaks=NULL){
  if(is.null(breaks)){
    breaks <- quantile(x, c(seq(0,.8,by=.2),.9, .95, .99, 1))
    if (sum(breaks==0)>1) { 
      temp <- which(breaks==0, arr.ind=TRUE)
      breaks <- breaks[max(temp):length(breaks)]
    }
  }
  x.discrete <- cut(x, breaks, include.lowest=TRUE)
  breaks.eng <- ifelse(breaks > 1000,
                       paste0(round(breaks/1000),'K'),
                       round(breaks))
  Labs <- paste(breaks.eng[-length(breaks.eng)], breaks.eng[-1],
                sep='-')
  levels(x.discrete) <- Labs
  return(x.discrete)
}

d.cty <- filter(ann2012full, agglvl_code==70)%.%
  select(state,county,abb, avg_annual_pay, annual_avg_emplvl)%.%
  mutate(wage=Discretize(avg_annual_pay),
         empquantile=Discretize(annual_avg_emplvl))


#Visualizing geographical distributions of pay
state_df <- map_data('state')
county_df <- map_data('county')

transform_mapdata <- function(x){
  names(x)[5:6] <- c('state','county')
  for(u in c('state','county')){
    x[,u] <- sapply(x[,u],simpleCap)
  }
  return(x)
}
state_df <- transform_mapdata(state_df)
county_df <- transform_mapdata(county_df)


chor <- left_join(state_df, d.state, by='state')
ggplot(chor, aes(long,lat,group=group))+
  geom_polygon(aes(fill=wage))+geom_path(color='black',size=0.2)+ scale_fill_brewer(palette='PuRd') +
  theme(axis.text.x=element_blank(), axis.text.y=element_blank(), axis.ticks.x=element_blank(), axis.ticks.y=element_blank())

chor <- left_join(county_df, d.cty)
ggplot(chor, aes(long,lat, group=group))+
  geom_polygon(aes(fill=wage))+
  geom_path( color='white',alpha=0.5,size=0.2)+
  geom_polygon(data=state_df, color='black',fill=NA)+
  scale_fill_brewer(palette='PuRd')+
  labs(x='',y='', fill='Avg Annual Pay')+
  theme(axis.text.x=element_blank(), axis.text.y=element_blank(), axis.ticks.x=element_blank(), axis.ticks.y=element_blank())


#Exploring where the jobs are, by industry
d.sectors <- filter(ann2012full, industry_code %in% c(11,21,54,52),
                    own_code==5, # Private sector 
                    agglvl_code == 74 # county-level
) %.%
  select(state,county,industry_code, own_code,agglvl_code,  
         industry_title, own_title, avg_annual_pay, 
         annual_avg_emplvl)%.%
  mutate(wage=Discretize(avg_annual_pay),
         emplevel=Discretize(annual_avg_emplvl))
d.sectors <- filter(d.sectors, !is.na(industry_code))

chor <- left_join(county_df, d.sectors)
ggplot(chor, aes(long,lat,group=group))+
  geom_polygon(aes(fill=emplevel))+
  geom_polygon(data=state_df, color='black',fill=NA)+
  scale_fill_brewer(palette='PuBu')+
  facet_wrap(~industry_title, ncol=2, as.table=T)+
  labs(fill='Avg Employment Level',x='',y='')+
  theme(axis.text.x=element_blank(), axis.text.y=element_blank(),   
        axis.ticks.x=element_blank(), axis.ticks.y=element_blank())


#Animating maps for geospatial time series
zipfile <- "2003_annual_singlefile.zip"
unzip(file.path('data',zipfile), exdir='data') # unzips the file
csvfile <- gsub('zip','csv', zipfile) # Change file name
csvfile <- gsub('_','.',csvfile) # Change _ to . in name
dat <- fread(file.path('data', csvfile)) # read data

dat <- left_join(dat, myarea)

dat <- filter(dat, agglvl_code==70) %.% # County-level aggregate
  select(state, county, avg_annual_pay) # Keep variables

get_data <- function(zipfile){
  unzip(file.path('data',zipfile), exdir='data') # unzips the file
  csvfile <- gsub('zip','csv', zipfile) # Change file name
  csvfile <- gsub('_','.',csvfile) # Change _ to . in name
  dat <- fread(file.path('data', csvfile)) # read data
  dat <- left_join(dat, myarea)
  dat <- filter(dat, agglvl_code==70) %.% # County-level aggregate
    select(state, county, avg_annual_pay) # Keep variables
  return(dat)
}

files <- dir('data', pattern='annual_singlefile.zip') # file names
n <- length(files)
dat_list <- vector('list',n) # Initialize the list
for(i in 1:n){
  dat_list[[i]]<- get_data(files[i])  # ingest data
  names(dat_list)[i] <- substr(files[i],1,4) #label list with years  
}

annpay <- ldply(dat_list) # puts all the data together
breaks <- quantile(annpay$avg_annual_pay,    
                   c(seq(0,.8,.2),.9,.95,.99,1)) # Makes a common set of breaks

mychoro <- function(d, fill_label=''){
  # d has a variable "outcome" that 
  # is plotted as the fill measure
  chor <- left_join(county_df, d)
  plt <- ggplot(chor, aes(long,lat, group=group))+
    geom_polygon(aes(fill=outcome))+    
    geom_path(color='white',alpha=0.5,size=0.2)+
    geom_polygon(data=state_df, color='black',fill=NA)+
    scale_fill_brewer(palette='PuRd')+
    labs(x='',y='', fill=fill_label)+
    theme(axis.text.x=element_blank(), axis.text.y=element_blank(), 
          axis.ticks.x=element_blank(),axis.ticks.y=element_blank())
  return(plt)
}

plt_list <- vector('list',n)
for(i in 1:n){
  dat_list[[i]] <- mutate(dat_list[[i]],                               
                          outcome=Discretize(avg_annual_pay,breaks=breaks))
  plt_list[[i]] <-
    mychoro(dat_list[[i]])+ggtitle(names(dat_list)[i])
}

choroplethr_animate(plt_list)


#Benchmarking performance for some common tasks
system.time(fread('data/2012.annual.singlefile.csv'))

library(rbenchmark)
opload <- benchmark(
  CSV=read.csv('data/2012.annual.singlefile.csv', 
               stringsAsFactors=F),
  CSVZIP=read.csv(unz('data/2012_annual_singlefile.zip',
                      '2012.annual.singlefile.csv'), stringsAsFactors=F),
  LOAD = load('data/ann2012full.rda'),
  FREAD = fread('data/2012.annual.singlefile.csv'),
  order='relative', # Report in order from shortest to longest 
  replications=1
)

ann2012full_dt <- data.table(ann2012full, key='industry_code')
industry_dt <- data.table(industry, key='industry_code')
op <- benchmark(
  DT = data.table::merge(ann2012full_dt, industry_dt,
                         by='industry_code', all.x=T),
  PLYR = plyr::join(ann2012full, industry,         
                    by='industry_code',type='left'),
  DPLYR = dplyr::left_join(ann2012full, industry),
  DPLYR2 = dplyr::left_join(ann2012full_dt, industry_dt),
  MERGE = merge(ann2012full, industry,
                by='industry_code', all.x=T),
  order='relative',
  replications=1
) 





































