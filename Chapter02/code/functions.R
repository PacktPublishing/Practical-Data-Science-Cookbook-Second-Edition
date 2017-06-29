# Utility functions

findvar <- function(str){
  # This function takes a string and finds all variables in the data
  # that have annotations matching that string. It returns both the 
  # variable names and their annotations
  # e.g. findvar('MPG') 
	labels[grep(str, labels[,2], ignore.case=TRUE),]
}

annot <- function(str){
  # This function takes a variable name and returns its annotation
  varnames = labels[,1]
  if(!(str %in% varnames)) stop('Variable not in annotations')
  labels[labels[,1]==str,2]
}