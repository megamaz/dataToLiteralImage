import os, zipfile, math, argparse
from PIL import Image

markers = {
    "NAMEEND":[0, 0, 255],
    "TERMINATOR":[84, 69, 82, 77, 73, 78, 65, 84, 79, 82, 0, 0]
}



def toImage(filetoimage, output="data.png", compress=True):
    imageDataFileName = "temp.zip" if compress else filetoimage
    if compress:
        with zipfile.ZipFile(imageDataFileName, mode='w', compression=zipfile.ZIP_DEFLATED) as tempZip:
            tempZip.write(filetoimage)
            tempZip.close()

    with open(imageDataFileName, 'rb') as rb:
        filenameToPixelList = [ord(l) for l in filetoimage]
        if len(filenameToPixelList)%3 != 0:
            filenameToPixelList += [0,]*(3-(len(filenameToPixelList)%3))

        byteData = [x for x in rb.read()]
        if len(byteData+filenameToPixelList)%3 != 0:
            byteData += [0,]*(3-(len(byteData)%3))

        data = filenameToPixelList + markers["NAMEEND"] + byteData + markers["TERMINATOR"]
        pixels = []
        currentPix = []
        for x in range(len(data)):
            currentPix.append(data[x])
            if (x+1)%3 == 0:
                currentPix = (currentPix[0], currentPix[1], currentPix[2])
                pixels.append(currentPix)
                currentPix = []
        
        xSize = int(math.sqrt(len(pixels))+1)
        ySize = int(math.sqrt(len(pixels))+1)
        img = Image.new("RGB", (xSize, ySize))
        try:
            for y in range(ySize):
                for x in range(xSize):
                    img.putpixel((x, y), pixels[x+(ySize*y)])
            if x+(ySize*y) != len(pixels)-1:
                print("missing data")
        except IndexError:
            pass

        except Exception as e:
            print(f"error: {e}")
        finally:
            img.save(output)
            del rb
    os.remove(imageDataFileName)

def fromImage(imageToFile, overWriteOutputNameto=None, fromcompressed=True):
    image:Image.Image = Image.open(imageToFile)

    filename = ""
    data = []
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pix = image.getpixel((x, y))
            data.append(pix)
    pixelDataStartIndex = 0
    for d in range(len(data)):
        if [*data[d],] == markers["NAMEEND"]:
            pixelDataStartIndex = d+1
            break

        filename += chr(data[d][0]) + chr(data[d][1]) + chr(data[d][2])

    filename = ''.join([x for x in filename if x != chr(0)])
    

    with open("temp_from.zip", 'wb') as wb:
        for i in range(pixelDataStartIndex, len(data)):
            if [*data[i]] + [*data[i+1]] + [*data[i+2]] + [*data[i+3]] == markers["TERMINATOR"]:
                break
            wb.write(data[i][0].to_bytes(1, "big"))
            wb.write(data[i][1].to_bytes(1, "big"))
            wb.write(data[i][2].to_bytes(1, "big"))

        wb.close()

    currentZipFileData = open("temp_from.zip", 'rb').read()
    if currentZipFileData[-3:] == markers["TERMINATOR"][:3]:
        newByteData = [x for x in open("temp_from.zip", 'rb').read()][:-3]
        
        with open("temp_from.zip", 'wb') as fixErrors:
            for b in newByteData:
                fixErrors.write(b.to_bytes(1, "big"))
    
    if fromcompressed:
        with zipfile.ZipFile("temp_from.zip") as unzip:
            unzip.extractall("./temp")
    else:
        os.rename("./temp/temp_from.zip", f"./temp/{filename}")
    
    oldName = filename
    newName = overWriteOutputNameto if overWriteOutputNameto else filename
    originalContents = open(f"./temp/{oldName}", 'rb').read()

    open(f"./{newName}", 'wb').write(originalContents)
    
    os.remove(f"./temp/{oldName}")
    os.rmdir("./temp")
    os.remove("temp_from.zip")
    
class IncorrectArgumentError(Exception):
    pass
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--toimage", help="The file you want to convert to image.")
    parser.add_argument("--imagename", help="The outputed image name. Defaults to data.png")
    parser.add_argument("--fromimage", help="Converts an image to a file.")
    parser.add_argument("--filename", help="The outputed file name. Defaults to the original filename used when converting original file to image.")
    parser.add_argument("--compress", help="Disables compression when doing data to image, or unpacks image as compressed data", action="store_true")
    args = parser.parse_args()

    # if no arguments passed
    if not any([args.toimage, args.imagename, args.fromimage, args.filename, args.compress]):
        currentFileName = __file__.split("\\")[-1]
        print(f"This script works off of launch arguments. do '{currentFileName} --help' to understand how to use them")

    # if output image name is specified but not file
    if args.imagename and not args.toimage:
        raise IncorrectArgumentError("The passed arguments were incorrect.")

    # if output file name but not image name
    if args.filename and not args.fromimage:
        raise IncorrectArgumentError("The passed arguments were incorrect.")
    
    if args.toimage:
        out = 'data.png' if not args.imagename else args.imagename
        toImage(args.toimage, out, not args.compress)
    
    if args.fromimage:
        out = None if not args.filename else args.filename
        fromImage(args.imagename, out, args.compress)
