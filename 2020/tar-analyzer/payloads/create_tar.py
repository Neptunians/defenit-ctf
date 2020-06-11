import tarfile

tar = tarfile.open("n4.tar", "w")
for i in range(1,5000):
    tar.add("../../config.yaml")

tar.close()
