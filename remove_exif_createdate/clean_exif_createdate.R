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
#folder <- "nmnh-botany-20170917-embed-meta-fix-01"

path <- paste(letter, folder, sep="")

#get list of tif files
file.names <- dir(path, pattern ="*.tif")

#remove old md5 file, if it exists
md5_file <- paste(path, "/", folder, ".md5", sep = "")
if (file.exists(md5_file)){
  unlink(md5_file)  
}


#main function
cleanexif <- function(file_i, ...){
  
  library(exifr)
  library(tools)
  
  #Get args
  args <- list(...)
  path = args[['path']]
  folder = args[['folder']]
  md5_file = args[['md5_file']]
  
  #Iterate over each file
  this_file <- paste(path, file_i, sep = "/")
  
  print(paste(format(Sys.time(), "%Y%m%d_%H%M%S"), ":", file_i, sep = ""))
  #Copy file to local folder
  file.copy(this_file, file_i)
  
  #check exif data
  exifinfo <- read_exif(file_i)
  
  #if there is a value in CreateDate, delete it using exiftool
  # then, save MD5 hash of new file
  if (hasName(exifinfo, "CreateDate")){
    #clean exif
    exiftool_call(args = c("-CreateDate="), fnames = file_i)
    unlink(this_file)
    #get MD5 hash
    md5_list <- data.frame(md5hash =  md5sum(file_i), file = file_i)
    #md5_list <- paste(md5sum(file_i), file_i, "\n", sep = " ")
    #move fixed file to original location on share
    file.rename(file_i, this_file)
    
  }else{
    #get MD5 hash
    md5_list <- data.frame(md5hash =  md5sum(this_file), file = file_i)
    #md5_list <- paste(md5sum(file_i), file_i, "\n", sep = " ")
  }
  
  #delete local file
  unlink(file_i)
  #delete temp file from exiftool
  unlink(paste(file_i, "_original", sep = ""))
  
  #save MD5 value to file
  #write.table(md5_list, file = md5_file, append = TRUE, quote = FALSE, row.names = FALSE, col.names = FALSE, sep = " ")
  return(md5_list)
}

#Debug file
start_time <- format(Sys.time(), "%Y%m%d_%H%M%S")
debug_file <- paste("debug_", start_time, ".txt", sep = "")

#save start date/time to debug file
sink(debug_file, append = FALSE)
cat(paste("Started on:", format(Sys.time(), "%Y%m%d_%H%M%S")))
sink()

# Number of cores, leaving 1 out
no_cores <- detectCores() - 1

#set cluster
cl <- makeCluster(no_cores, outfile = debug_file, type = "PSOCK")

#execute function on cluster
res <- parLapply(cl, file.names, cleanexif, path = path, folder = folder, md5_file = md5_file)

write.table(do.call(rbind.data.frame, res), file = md5_file, append = FALSE, quote = FALSE, row.names = FALSE, col.names = FALSE, sep = " ")

#stop cluster
stopCluster(cl)

#save finish date/time to debug file
sink(debug_file, append = TRUE)
cat(paste("\nFinished on:", format(Sys.time(), "%Y%m%d_%H%M%S")))
sink()