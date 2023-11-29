## JHOVE memory limit

The main JHOVE script doesn't have an argument to limit the amount of RAM it will use. This causes problems in the cluster. To limit the memory, edit the last line in the `jhove` file from:

```
java -Xss1024k -classpath "${CP}" edu.harvard.hul.ois.jhove.Jhove -c "${CONFIG}" "${@}"
```

to: 

```
java -server -Xmx2G -Xss1024k -classpath "${CP}" edu.harvard.hul.ois.jhove.Jhove -c "${CONFIG}" "${@}"
```

Where `2G` is how much memory, in this case, 2GB. 