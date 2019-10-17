#Script to run over the list of files in a folder, check the CreateDate
# field, clear it, and store the MD5 hash of the files.
#
# May 2018

#library(exifr)
library(tools)
library(parallel)

#set homefolder
setwd("~/GitHub/DPO_informatics")

#Network share letter
letter <- "J:/"

#folder to work on
#folder <- "nmnh-botany-20170917-embed-meta-fix-04"

path <- paste(letter, folder, sep="")

#get list of tif files
file.names <- dir(path, pattern ="*.tif")

#main function
checkexif <- function(file_i, ...){
  
  library(exifr)
  library(tools)
  
  #Get args
  args <- list(...)
  path = args[['path']]
  folder = args[['folder']]
  
  #Iterate over each file
  this_file <- paste(path, file_i, sep = "/")
  
  print(paste(format(Sys.time(), "%Y%m%d_%H%M%S"), ":", file_i, sep = ""))
  
  #check exif data
  exifinfo <- read_exif(this_file)
  
  #if there is a value in CreateDate, delete it using exiftool
  # then, save MD5 hash of new file
  if (hasName(exifinfo, "CreateDate")){
    date_data <- data.frame(date = exifinfo$CreateDate, file = file_i)
  }else{
    date_data <- data.frame(date = "none", file = file_i)
  }
  
  return(date_data)
}

#Debug file
start_time <- format(Sys.time(), "%Y%m%d_%H%M%S")
debug_file <- paste("logs/verify_", start_time, ".txt", sep = "")

#save start date/time to debug file
sink(debug_file, append = FALSE)
cat(paste("Started on:", format(Sys.time(), "%Y%m%d_%H%M%S")))
sink()

# Number of cores, leaving 1 out
no_cores <- detectCores() - 1

#set cluster
cl <- makeCluster(no_cores, outfile = debug_file, type = "PSOCK")

#execute function on cluster
res <- parLapply(cl, file.names, checkexif, path = path, folder = folder)

write.table(do.call(rbind.data.frame, res), file = paste(folder, "_verify.txt", sep = ""), append = FALSE, quote = FALSE, row.names = FALSE, col.names = FALSE, sep = " ")

#stop cluster
stopCluster(cl)

#save finish date/time to debug file
sink(debug_file, append = TRUE)
cat(paste("\nFinished on:", format(Sys.time(), "%Y%m%d_%H%M%S")))
sink()