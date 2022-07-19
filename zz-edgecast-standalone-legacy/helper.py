import os
import zipfile


def zipdir(path, ziph, verbose=False):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if '.zip' not in file: 
                if verbose: print("Zipping", os.path.join(root, file))
                ziph.write(os.path.join(root, file))

def CreateZip(filename, verbose=False):
    try:
        os.remove(zipfileName)
    except:
        pass
    zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    zipdir('.', zipf, verbose=verbose)
    zipf.close()
    # end CreateZip
    