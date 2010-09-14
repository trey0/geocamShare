#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

##############################################################################
#Test Python script for creating svg files
#Alex Roederer, geocam project
#IMPORTANT:
#ENSURE THAT THE IMAGES YOU ARE RUNNING THIS SCRIPT ON HAVE: 
#BEEN CONVERTED ENTIRELY TO PATHS (PATH>OBJECT TO PATH)
#HAVE HAD THEIR DEVS VACUUMED (FILE>VACUUM DEFS)
#AND HAVE BEEN SIMPLIFIED (PATH>SIMPLIFY) TO ENSURE PROPER CONVERSION
##############################################################################
import os
import optparse
import re

from math import sqrt

import xml
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
##############################################################################
def getAttributeData(tag, attribute):
    """
    Given a tag and an attribute, returns the value of that attribute
    within the tag, or None if that attribute is not found in the tag.
    """
    regExpression = re.compile('[ \n]+' + attribute + ' *= *"(.*)"')

    matchOb = regExpression.search(tag[1])
    if matchOb != None:
        data = matchOb.group(1)
    else:
        data = None
    return data
##############################################################################
def parseNextTag(fileHandle):
    """
    Gets the next tag found in the file linked to the provided file handle
    returns a tag structure: a list containing the name of the tag and 
    the full tag text.
    """
    regExpression = re.compile('<([^>]*)[\n|>]+')
    tagName = ''
    finishedTag = ''
    tagList = []
    matchOb = None

    while matchOb == None:
        try: 
            line = fileHandle.next()
        except StopIteration:
            return None
        matchOb = regExpression.search(line)

    tagName = matchOb.group(1)

    if '>' in line:
        finishedTag += line
    else:
        while not '>' in line:
            finishedTag += line#.rstrip('\n')
            try:
                line = fileHandle.next()
            except StopIteration:
                break
        finishedTag += line#.rstrip('\n')

    tagName = tagName.strip("\n")

    #contains the tag name and all tag text
    tagList.append(tagName)
    tagList.append(finishedTag)
    return tagList

##############################################################################
def parseNextTagText(text):
    """
    Gets the next tag found in the provided text
    returns a tag structure (a list containing the name of the tag and 
    the full tag text) and the remainder of the text.
    """
    regExpression = re.compile('<([^\s>]+)([\s\S]*)>')
    tagName = ''
    finishedTag = ''
    tagList = []
    matchOb = None
    line = ''
    
    textLines = text.split('\n')
    
    while matchOb == None:
        try: 
            line += textLines.pop(0) + '\n'
        except IndexError:
            return None, None
        matchOb = regExpression.search(line.strip('\n '))

    tagName = matchOb.group(1)
    rest = matchOb.group(2)

    finishedTag = '<' + tagName + rest + '>'

    tagName = tagName.strip("\n ")

    #contains the tag name and all tag text
    tagList.append(tagName)
    tagList.append(finishedTag)

    remainingText = text.split(finishedTag, 1)

    return tagList, remainingText[1]

##############################################################################
def getTag(fileHandle, tagName):
    """
    Gets the first tag with the specified tagName from the specified file 
    accessable through fileHandle. Returns a list representing the tag 
    (name of the tag and the full tag text) or None if the tag is not
    found in the document.
    """
    tag = parseNextTag(fileHandle)
    while tag != None:
        if tag[0] == tagName:
            return tag
        else:
            tag = parseNextTag(fileHandle)  
    return None
##############################################################################
def getTagText(text, tagName):
    """
    Gets the first tag with the specified tagName from the provided text 
    Returns a list representing the tag (name of the tag and the full 
    tag text) or None if the tag is not found. 
    """
    
    tag, remainder = parseNextTagText(text)
    while tag != None:
        if tag[0] == tagName:
            return tag
        else:
            tag, remainder = parseNextTagText(remainder)  
    return None
##############################################################################
def getTagWithID(fileHandle, tagName, idValue):
    """
    Gets the tag with the specified tagName and having the specified idValue
    as the value of its "id" attribute. Returns a list representing the
    tag (name of the tag and the full tag text) or None if the tag is not
    found.
    """

    tag = getTag(fileHandle, tagName)

    while tag != None:
        data = getAttributeData(tag, 'id')
        if data == idValue:
            return tag
        else:
            tag = getTag(fileHandle, tagName)
    return None
##############################################################################
def getDocumentDimensions(fileHandle):
    """
    Returns the width and height of the document expressed in the
    file attached to the provided file handle.
    These values are taken from the "width" and "height" attributes of the
    "svg" tag.
    """

    tag = parseNextTag(fileHandle)
    width = 0 
    height = 0
    regExpressionWidth = re.compile('width= *"([0-9]*\.*[0-9]+)"')
    regExpressionHeight = re.compile('height= *"([0-9]+\.*[0-9]+)"')
    
    while tag != None:
        if tag[0] == 'svg':
            matchOb = regExpressionWidth.search(tag[1])
            if matchOb != None:
                width = float(matchOb.group(1))
            else:
                print "Error getting width!"
            matchOb = regExpressionHeight.search(tag[1])
            if matchOb != None:
                height = float(matchOb.group(1))
            else:
                print "Error getting height!"
            tag = None
        tag = parseNextTag(fileHandle)

    return width, height
#############################################################################
def setDocumentDimensions(fileHandle, fileOut, width, height):
    """
    Sets the dimensions of the document page to the given width and height
    by changing the attributes of the 
    """

    tag = parseNextTag(fileHandle)
    regExpressionWidth = re.compile('width= *"([0-9]*\.*[0-9]+)(.*)"')
    regExpressionHeight = re.compile('height= *"([0-9]+\.*[0-9]+)(.*)"')

    while tag != None:
        if tag[0] == 'svg':
            tag, oldValW = changeAttribute(tag, 'width', width)
            tag, oldValH = changeAttribute(tag, 'height', height)
        fileOut.write(tag[1])
        
        tag = parseNextTag(fileHandle)

    return 1
#############################################################################
def getMainGroupContents(fileHandle):
    """
    Gets the content of the "main group"; data located in the first <g> tag
    that represents the document's contents. Returns these contents as a
    string. 
    """

    tag = parseNextTag(fileHandle)
    tagCount = 0
    source = ''

    while tag != None:
        if tag[0] == 'g':
            tagCount += 1
            while tagCount != 0 and tag != None:
                tag = parseNextTag(fileHandle)
                if tag[0] == 'g':
                    tagCount += 1
                if tag[0] == '/g':
                    tagCount -= 1
                if tagCount > 0:
                    source = source + tag[1]
        tag = parseNextTag(fileHandle)

    return source
#############################################################################
def changeAttribute(tag, attribute, newValue):
    """
    Changes the specified attribute in the specified tag to have the value
    newValue. Returns the newly changed tag and the previous value of the 
    attribute. 
    """

    regExpression = re.compile('<' + tag[0] + '([^>]* )' + 
        attribute + '= *"(.*)"')

    matchOb = regExpression.search(tag[1])

    if matchOb != None:
        oldValue = matchOb.group(2)
        resultingString = regExpression.sub(r'<' + tag[0] 
            + r'\1' + attribute + r'="' + str(newValue) + '"', tag[1]);
        #The semicolon is only necessary to prevent vim from miscoloring 
        #the text after a sub expression. Should be using emacs... 
        tag[1] = resultingString
        return tag, oldValue
    else:
        return None, None 
#############################################################################
def changeAllAttributesInText(text, attribute, newValue, append):
    """
    Changes the specified attribute in all tags in the provided text to the 
    value provided in newValue. If append is 0, the value will be replaced. 
    If append is anything else, the value will be appended to the end
    of the old attribute value. 
    Returns a string containing the edited text. 
    """

    regExpression = re.compile(r'([ \n]*)' + attribute + r'= *"(.*)"')

    if append == 0:
        resultingString = regExpression.sub(r'\1' + attribute 
        + r'="' + newValue + '"', text);
    else:
        resultingString = regExpression.sub(r'\1' + attribute 
        + r'="\2' + newValue + '"', text);
    return resultingString
##############################################################################
def insertAttribute(tag, attribute, newValue):
    """
    Inserts the specified attribute in the specified tag, with the value 
    newValue. 
    (The attribute is inserted as the last attribute in the tag). 
    """

    value = re.sub(r'([/])>', '\n    ' + attribute + '="' + newValue 
        + '" \1>\n    ', tag[1]);
    tag[1] = value

    return tag
##############################################################################
def insertAttributeInText(text, tagWanted, attribute, newValue):
    """
    Inserts the specified attribute in the specified tag, with the value 
    newValue, in the text provided. Returns the text with the modified tag.
    """

    newTag =  insertAttribute(tagWanted, attribute, newValue)
    if newTag != None:
        re.sub(r'<' + tagWanted[0] + r'[^>]*>', newTag[1], text);
    else:
        return None

    return text
##############################################################################
def insertTextChunkAfterTag(textToInsert, tagFind, oldFile, newFile):
    """
    Prints the oldFile to the newFile, until tagFind is found in the file. 
    Then, the textToInsert is printed to the newFile, and the tag that was
    found is returned. 
    """

    firstTagFound = 0
    tag = parseNextTag(oldFile)
    while tag != None and firstTagFound == 0:
        if tag[0] == tagFind:
            newFile.write(tag[1])   
            newFile.write(textToInsert)
            firstTagFound = 1
        else:
            newFile.write(tag[1])
            tag = parseNextTag(oldFile)
#    newFile.write(tag[1])   
    return firstTagFound
##############################################################################
def copyFile(oldFile, newFile):
    """
    Copies the tags from the oldFile to the newFile, until the last tag of
    the oldFile is reached and copied. Should always return None. 
    """

    tag = parseNextTag(oldFile)
    while tag != None:
        newFile.write(tag[1])
        tag = parseNextTag(oldFile)
    return tag 
##############################################################################
def computeHSL(hexValue):
    """
    Given a six-digit hex code (no #), compute the hue, saturation, and 
    luminosity. Returns a list consisting of the hue, saturation, and 
    luminosity values. Hue is a (float?) between 0 and 360, luminosity and 
    saturation floats between 0 and 1
    """

    red = int('0x' + hexValue[0:2], 16)
    green = int('0x' + hexValue[2:4], 16)
    blue = int('0x' + hexValue[4:6], 16)

    redF = float(red) / 255
    greenF = float(green) / 255
    blueF = float(blue) / 255

    colorList = [redF, greenF, blueF]
    maxColor = max(colorList)
    minColor = min(colorList)

    L = maxColor + minColor / 2

    if maxColor == minColor:
        S = 0
        H = 0
    else:
        if L < .5:
            S = (maxColor-minColor)/(maxColor+minColor)
        else:
            S = (maxColor-minColor)/(2-maxColor-minColor)
        if redF == maxColor:
            H = (greenF-blueF)/(maxColor-minColor)
        elif green == maxColor:
            H = 2 + (blueF-redF)/(maxColor-minColor)
        else:
            H = 4 + (redF-greenF)/(maxColor-minColor)

        H = (H / 6) * 360

    return [H, S, L]
##############################################################################
def changeAllColor(text, color):
    """
    Change all hex color values in a certain string of text to the provided
    color (which is a six character string whose characters are hexadecimal) 
    Returns the text with modifications made. 
    """

    regularExpression = re.compile(r':#([0-9A-Fa-f]{6})[;|"]')
    regularExpressionFilter = re.compile(r':url\(.*\)[;|"]')

    matchOb = regularExpression.search(text)
    matchObFilter = regularExpressionFilter.search(text)

    newData = None

    if matchOb != None:
        newData = re.sub(r':#[0-9A-Fa-f]{6}', r':#' + color, text);
        newData = re.sub(r';stroke:none', r';stroke:#' + color, newData);
        newData = re.sub(r';fill:none', r';fill:#' + color, newData);
    else:
        newData = text
    if matchObFilter !=None: 
        newData = re.sub(r':url\(.*\)', r':#' + color, newData); 

    return newData
##############################################################################
def changeAllStroke(text, stroke):
    """
    Change all stroke widths in a given string of text to the provided width
    Returns the text with modifications made. 
    """
    
    newData = ''
    regularExpressionTransform = re.compile(r'matrix\(([^,]*),([^,]*)' 
        + r',([^,]*),([^,]*)(,[^,]*,[^,]*)\)')

    stroke = float(stroke)

    tag, remainder= parseNextTagText(text)

    #Loop through the tags in the text
    while tag != None:
        #Attempt to find a transform, if one exists
        attributeData = getAttributeData(tag, 'transform')
        if attributeData != None:
            matchOb = regularExpressionTransform.search(attributeData)
            if matchOb != None: 
                #If there is a transform, scale the desired stroke to a 
                #value that, when the transform is applied, will bring the
                #stroke back to the original value
                newStroke = stroke/sqrt(abs(float(matchOb.group(1))
                    *float(matchOb.group(4))-
                    float(matchOb.group(2))*float(matchOb.group(3))))
            else: 
                newStroke = stroke
        else: 
            newStroke = stroke
        #Substitute the new stroke in that tag
        newData += re.sub(r'stroke-width:[0-9]*[.]?[0-9]+', r'stroke-width:' 
            + str(newStroke), tag[1]);
        #Get the next tag
        tag, remainder = parseNextTagText(remainder)

    return newData
##############################################################################
def changeStrokeOpacity(text, opacity):
    """
    Change all stroke opacities in a given string of text to the provided
    opacity. Returns the text with modifications made. 
    """

    newData = None
    regularExpression = re.compile(r'stroke-opacity:[0-9]*[.]?[0-9]+[;|"]');
    matchOb = regularExpression.search(text)
    if matchOb != None:
        newData = re.sub(r'stroke-opacity:[0-9]*[.]?[0-9]+', 
            r'stroke-opacity:' + opacity, text);
    else:
        newData = text

    return newData
##############################################################################
def changeFillOpacity(text, opacity):
    """
    Change all stroke opacities in a given string of text to the provided
    opacity. Returns the text with modifications made. 
    """ 

    newData = None
    regularExpression = re.compile(r'fill-opacity:[0-9]*[.]?[0-9]+[;|"]');
    matchOb = regularExpression.search(text)
    if matchOb != None:
        newData = re.sub(r'fill-opacity:[0-9]*[.]?[0-9]+', r'fill-opacity:' 
            + opacity, text);
    else:
        newData = text

    return newData
##############################################################################
def changeAllPosition(fileHandle, newX, newY):
    """
    Transpose all items in the file provided by the fileHandle by newX and 
    newY units. (Looks for matrix transformations; if one exists for some 
    path, the transpose occurs on the last two elements of that matrix. 
    Otherwise, the transpose is applied directly to each of the nodes in the
    image's "d" tag. 
    """

    regularExpressionTransform = re.compile(r'matrix\(' 
        + '([^,]*,[^,]*,[^,]*,[^,]*,)(.*),(.*)\)')
    regularExpressionNumberPair = re.compile(r'([-]?[0-9]*[.]?[0-9]+),' 
        + '([-]?[0-9]*[.]?[0-9]+)');

    newData = ''
    tag= parseNextTag(fileHandle)

    while tag != None:

        transformFound = 0
        modifiedData = ''
        newDataToAdd = tag[1]
        attributeTransform = getAttributeData(tag, 'transform')
        #Case where there's a transform
        if attributeTransform != None:
            matchOb = regularExpressionTransform.search(attributeTransform)
            #It's a matrix transform (not just a scale)
            if matchOb != None: 
                beginning = matchOb.group(1)
                finalX = float(matchOb.group(2)) + newX
                finalY = float(matchOb.group(3)) + newY
                newDataToAdd = re.sub(r'matrix\(.*\)',r'matrix(' + beginning 
                    + str(finalX) + ',' + str(finalY) + ')', tag[1])
                transformFound = 1

        #No transform; change values of all number pairs in d tag
        if transformFound != 1:
            attributeDataD = getAttributeData(tag, 'd')
            if attributeDataD != None: 
                numberList = attributeDataD.split(' ')
                for numberPair in numberList:
                    matchOb = regularExpressionNumberPair.search(numberPair)
                    #If it is indeed a number pair:
                    if matchOb != None:
                        finalX = float(matchOb.group(1)) + newX
                        finalY = float(matchOb.group(2)) + newY
                        numberPair = str(finalX) + ',' + str(finalY)
                    modifiedData += numberPair + ' '
                newDataToAdd = re.sub('[ \n]d="[^"]*"',r' d="' + modifiedData 
                    + '"', tag[1])
            else:
                newDataToAdd = tag[1]

        newData += newDataToAdd 

        tag = parseNextTag(fileHandle)

    return newData
##############################################################################
def changeAllPositionText(text, newX, newY):
    """
    Transpose all items in the string provided by text by newX and 
    newY units. (Looks for matrix transformations; if one exists for some 
    path, the transpose occurs on the last two elements of that matrix. 
    Otherwise, the transpose is applied directly to each of the nodes in the
    image's "d" tag. 
    """

    regularExpressionTransform = re.compile('matrix\(([^,]*,[^,]*,[^,]*,' 
        + '[^,]*,)(.*),(.*)\)')
    regularExpressionNumberPair = re.compile(r'([-]?[0-9]*[.]?[0-9]+),'
        + '([-]?[0-9]*[.]?[0-9]+)');

    newData = ''

    tag, remainder= parseNextTagText(text)
    while tag != None:

        transformFound = 0
        modifiedData = ''

        newDataToAdd = tag[1]

        attributeTransform = getAttributeData(tag, 'transform')
        #Case where there's a transform
        if attributeTransform != None:
            matchOb = regularExpressionTransform.search(attributeTransform)
            #It's a matrix
            if matchOb != None: 
                beginning = matchOb.group(1)
                finalX = float(matchOb.group(2)) + newX
                finalY = float(matchOb.group(3)) + newY
                newDataToAdd = re.sub(r'matrix\(.*\)',r'matrix(' 
                    + beginning + str(finalX) + ',' +str(finalY)+ ')', tag[1])
                transformFound = 1

        #No transform; change values of all number pairs in d tag
        if transformFound != 1:
            attributeDataD = getAttributeData(tag, 'd')
            if attributeDataD != None:
                numberList = attributeDataD.split(' ')
                for numberPair in numberList:
                    matchOb = regularExpressionNumberPair.search(numberPair)
                    #If it is indeed a number pair:
                    if matchOb != None:
                        finalX = float(matchOb.group(1)) + newX
                        finalY = float(matchOb.group(2)) + newY
                        numberPair = str(finalX) + ',' + str(finalY)
                    modifiedData += numberPair + ' '                    
                newDataToAdd = re.sub(r'[ \n]d="[^"]*"',r' d="' 
                    + modifiedData + '"', tag[1])
            else:
                newDataToAdd = tag[1]

        newData += newDataToAdd + '\n'
        tag, remainder = parseNextTagText(remainder)

    return newData
##############################################################################
def turnToBW(attributeText):
    """
    Replaces the colors in attributeText to either black or white, depending 
    on the luminosity value of the color. 
    """

    regularExpression = re.compile(r':#([0-9A-Fa-f]{6})[;|"]') #"

    matchOb = regularExpression.search(attributeText)

    if matchOb != None:
        oldValue = matchOb.group(1)
        HSL = computeHSL(oldValue)
        if HSL[2] < .5 or (HSL[0] < 260 and HSL[0] > 190):
            replaceWith = '000000'
        else:
            replaceWith = 'FFFFFF'
        newData = re.sub(oldValue, replaceWith, attributeText);
        return newData
    else:
        return None
##############################################################################
def resizeCanvas(fileName, documentX, documentY, append):
    """
    Resizes the canvas by setting the document dimensions and changing the
    position of the items on the canvas. 
    Writes the new resized canvas and transposed contents to a new file. 
    The file's name is returned as a string. 
    """

    outputFileName = 'RENDERICONout' + append + '.svg'
    outputFileName2 = 'RENDERICON2out' + append + '.svg'

    try:
        iconResize = open(outputFileName, 'w')
        iconFileHandle = open(fileName, 'r')
    except IOError:
        print "Error Opening Files (rC)"

    setDocumentDimensions(iconFileHandle, iconResize, documentX*3, documentY*3)

    iconResize.close()
    iconFileHandle.close()

    try:
        iconResize = open(outputFileName,'r')
        iconResizeMove = open(outputFileName2, 'w')
    except IOError:
        print "Error Opening Files (4)"
    
    movedIcon = changeAllPosition(iconResize, documentX, documentY)
    iconResizeMove.write(movedIcon)

    iconResize.close()
    iconResizeMove.close()

    os.system('rm ' + outputFileName) 

    return outputFileName2
##############################################################################
def renderIcon(iconFileName, options=None, **kwargs):
    """
    Main function to initiate icon rendering. 
    """

    if options == None:
        options = parserG.get_default_values()
    for k, v in kwargs.iteritems():
        setattr(options, k, v)

    iconWithArrowFileName = os.path.splitext(os.path.basename(iconFileName))[0] + '000.svg'
    iconWithAandGlowFileName = os.path.splitext(os.path.basename(iconFileName))[0] + '-selected000.svg'
    iconWithAandBWFileName = os.path.splitext(os.path.basename(iconFileName))[0] + '-faded000.svg'
    iconWithAGandBWFileName = os.path.splitext(os.path.basename(iconFileName))[0] + '-fadedselected000.svg'

    try:
        arrowFileHandle = open(options.arrowFileName, 'r')
        iconFileHandle = open(iconFileName, 'r')
    except IOError:
        print "Unable to open file; bad file names"


    #Add arrow to file----
    try:
        iconWithArrowFileHandle = open(iconWithArrowFileName, 'w')
    except IOError:
        print "Unable to open file; bad file name"

    arrowSVGSource = ''
    tagCount = 0
    
    arrowFileHandle.seek(0)
    arrowSVGSource = getMainGroupContents(arrowFileHandle)

    arrowFileHandle.seek(0)
    width, height = getDocumentDimensions(iconFileHandle)
    arrowWidth, arrowHeight = getDocumentDimensions(arrowFileHandle) 

    #Moves the arrow to the correct position
    arrowSVGSource = changeAllPositionText(arrowSVGSource, 0, -.6 * height - float(options.distance))

    #Inserts the arrow XML into the new file
    iconFileHandle.seek(0)
    insertTextChunkAfterTag(arrowSVGSource, 'g', 
    iconFileHandle, iconWithArrowFileHandle)

    #Copies the rest of the file over
    copyFile(iconFileHandle, iconWithArrowFileHandle)    

    iconFileHandle.close()
    arrowFileHandle.close()
    iconWithArrowFileHandle.close()


    #Creates the icon with glow----
    #Makes a copy of the newly created "Arrow+Icon" file, and inserts
    #glow below it. Also inserts a drop shadow beneith the glow. 
    try:
        iconWithArrowFileHandle = open(iconWithArrowFileName, 'r')    
        iconWithAandGlowFileHandle = open(iconWithAandGlowFileName, 'w')
    except IOError:
        print "Error Opening Files (2)"
    
    #To make it "glow," duplicate the image, then apply a blur filter
    blurFilter = '''    <filter
          inkscape:collect="always"
          id="filterAUTOADDBLUR"
          x="-0.45460767"
          width="1.9092153"
          y="-0.29729332"
          height="1.5945866">
          <feGaussianBlur
            inkscape:collect="always"
            stdDeviation="6"
            id="feGaussianBlurAUTOADD" />
        </filter>
        '''

    blurFilterStyle = 'filter:url(#filterAUTOADDBLUR);'

    iconWithArrowFileHandle.seek(0)
    mainImageInfo = getMainGroupContents(iconWithArrowFileHandle)

    shadowMainImageInfo = mainImageInfo

    #Drop Shadow
    shadowMainImageInfo = changeAllColor(shadowMainImageInfo, '000000')
    shadowMainImageInfo = changeAllPositionText(shadowMainImageInfo, 40, 40) 
    shadowMainImageInfo = changeFillOpacity(shadowMainImageInfo, '.8')
    shadowMainImageInfo = changeStrokeOpacity(shadowMainImageInfo, '.8')
    
    #Outer Glow 
    newMainImageInfo = changeAllColor(mainImageInfo, 'ffffff')
    newMainImageInfo = changeAllStroke(newMainImageInfo, '70')

    #Should also change the id tags of everything to make them unique. 
    newMainImageInfo = changeAllAttributesInText(newMainImageInfo,'id','AUTOADDBLUR', 1) 
    #SHADOW
    shadowMainImageInfo = changeAllAttributesInText(shadowMainImageInfo, 'id', 'AUTOADDSHADOW', 1)
    
    #Add filter:url(#filterAUTOADD) to style tag of everything. 
    tag, restOfText = parseNextTagText(newMainImageInfo)
    temp = ''
    while tag != None:
        styleData = getAttributeData(tag, 'style')
        if styleData != None:
            tag, oldValue = changeAttribute(tag, 'style', blurFilterStyle 
                + styleData)
        temp += tag[1] + '\n'
        tag, restOfText = parseNextTagText(restOfText)

    newMainImageInfo = temp

    #Inserts the blur Filter
    iconWithArrowFileHandle.seek(0)
    insertTextChunkAfterTag(blurFilter, 'defs', 
    iconWithArrowFileHandle, iconWithAandGlowFileHandle)
    
    #Inserts the drop shadow. 
    insertTextChunkAfterTag(shadowMainImageInfo,'g', 
    iconWithArrowFileHandle, iconWithAandGlowFileHandle)

    #Inserts the glow
    iconWithAandGlowFileHandle.write(newMainImageInfo)
    
    #Copies the rest of the file
    copyFile(iconWithArrowFileHandle, iconWithAandGlowFileHandle)    

    iconWithAandGlowFileHandle.close()
    
    #----
    #Makes the Black and white copy of the icon:
    #The copy is the same as the original, but for the fact that all 
    #dark colors are changed to black, and all light colors changed to white
    try:
        iconWithArrowFileHandle = open(iconWithArrowFileName, 'r')    
        iconWithAandGlowFileHandle = open(iconWithAandGlowFileName, 'r')     
    except IOError:
        print "Error Opening Files (3)"

    try: 
        iconWithAandBWFileHandle = open(iconWithAandBWFileName, 'w')
        iconWithAGandBWFileHandle = open(iconWithAGandBWFileName, 'w')
    except IOError:
        print "Error Opening Files for writing (4)" 

    #Change fill and stroke values in "style" tag
    #Might as well go through all the definitions and change
    #colors there, too (always style tags). 
    tag = parseNextTag(iconWithArrowFileHandle)
    while tag != None:
        atData = getAttributeData(tag, 'style')
        if atData != None:
            newData = turnToBW(atData)
            if newData != None:
                changeAttribute(tag, 'style', newData)
        iconWithAandBWFileHandle.write(tag[1])
        tag = parseNextTag(iconWithArrowFileHandle)

    tag = parseNextTag(iconWithAandGlowFileHandle)
    while tag != None:
        atData = getAttributeData(tag, 'style')
        if atData != None:
            newData = turnToBW(atData)
            if newData != None:
                changeAttribute(tag, 'style', newData)
        iconWithAGandBWFileHandle.write(tag[1])
        tag = parseNextTag(iconWithAandGlowFileHandle)

    #Cleanup
    iconWithArrowFileHandle.close()
    iconWithAandGlowFileHandle.close()
    iconWithAandBWFileHandle.close()
    iconWithAGandBWFileHandle.close()

    options.outputDir = options.outputDir.strip(' ') + '/'

    #Use the command line to convert the six files to .png 
    iconFileNameChanged = os.path.basename(iconFileName)
    iconFileNameChanged = os.path.splitext(iconFileNameChanged)[0]

    #------
    #Make the canvas bigger
    documentX = width + arrowWidth
    documentY = height + arrowHeight + float(options.distance)

    iWAFN = resizeCanvas(iconWithArrowFileName, documentX, documentY, '1')
    iWAGFN = resizeCanvas(iconWithAandGlowFileName, documentX, documentY, '2')
    iWABWFN = resizeCanvas(iconWithAandBWFileName, documentX, documentY, '3')
    iWAGBWFN = resizeCanvas(iconWithAGandBWFileName, documentX, documentY, '4')
    #------

    iconWithArrowFileNameChanged = os.path.splitext(os.path.basename(iconWithArrowFileName))[0] 
    iconWithAandGlowFileNameChanged = os.path.splitext(os.path.basename(iconWithAandGlowFileName))[0] 
    iconWithAandBWFileNameChanged = os.path.splitext(os.path.basename(iconWithAandBWFileName))[0] 
    iconWithAGandBWFileNameChanged = os.path.splitext(os.path.basename(iconWithAGandBWFileName))[0] 

    out = options.outputDir + iconFileNameChanged + '.png'
    os.system('convert -background transparent -trim -resize 32x32 ' 
              + iconFileName + ' ' + out)
    print 'svg rendered to %s' % out

    out = options.outputDir + iconFileNameChanged + 'Point.png'
    os.system('convert -background transparent -trim -resize 32x32 ' 
              + iWAFN + ' ' + out)
    print 'svg rendered to %s' % out
        
    if 0:
        #Make 16 px version
        os.system('convert -background transparent -trim -resize 16x16 ' 
                  + iconFileName + ' ' + options.outputDir + '/16/' 
                  + iconFileNameChanged + '.png')
        
        #Make 48 px versions
        os.system('convert -background transparent -trim -resize 48x48 ' 
                  + iconFileName + ' ' + options.outputDir + '/48/' 
                  + iconFileNameChanged + '.png')
        
        #Make 64 px versions
        os.system('convert -background transparent -trim -resize 64x64 ' 
                  + iWAFN + ' ' + options.outputDir + '/64/'
                  + iconWithArrowFileNameChanged + '.png')
        print "icon with arrow done"
        os.system('convert -background transparent -trim -resize 64x64 ' 
                  + iWAGFN + ' ' + options.outputDir + '/64/'
                  + iconWithAandGlowFileNameChanged + '.png')
        print "icon with arrow and glow done"
        os.system('convert -background transparent -trim -resize 64x64 ' 
                  + iWABWFN + ' ' + options.outputDir + '/64/'
                  + iconWithAandBWFileNameChanged + '.png')
        print "icon with arrow and black and white done"
        os.system('convert -background transparent -trim -resize 64x64 ' 
                  + iWAGBWFN + ' ' + options.outputDir + '/64/'
                  + iconWithAGandBWFileNameChanged + '.png')
        print "icon with arrow, glow, and black and white done"

    #Remove workfiles with expanded canvases
    os.system('rm ' + iWAFN) 
    os.system('rm ' + iWAGFN) 
    os.system('rm ' + iWABWFN) 
    os.system('rm ' + iWAGBWFN) 

    #Remove modified SVN files; leaves only png files. 
    os.system('rm ' + iconWithArrowFileName) 
    os.system('rm ' + iconWithAandGlowFileName) 
    os.system('rm ' + iconWithAandBWFileName) 
    os.system('rm ' + iconWithAGandBWFileName) 

def buildIcon(builder, iconFileName, **kwargs):
    outputDir = kwargs['outputDir']
    outBase = os.path.splitext(os.path.basename(iconFileName))[0] + '.png'
    builder.applyRule(dst=os.path.join(outputDir, outBase),
                      srcs=[iconFileName],
                      func=lambda: renderIcon(iconFileName, **kwargs))

##############################################################################
def main():
    (options, args) = parserG.parse_args()

    iconSVG = args[0]

    #EXCEPTIONHANDLING SHOULD BE PERFORMED HERE

    renderIcon(iconSVG, options)

##############################################################################
parserG = optparse.OptionParser("usage: %prog")

thisDir = os.path.dirname(os.path.realpath(__file__))
parserG.add_option('-a', '--arrow', dest='arrowFileName', 
                  help='Arrow File Directory',
                  default='%s/media/svgIcons/accessories/arrow.svg' % os.path.dirname(thisDir))
parserG.add_option('-d', '--distance', dest='distance', 
                  help='Positioning of Arrow File above icon', default=25)
parserG.add_option('-o', '--outputDir', 
                  help='Destination for produced png icons', default = './')


##############################################################################
if __name__ == "__main__":
    main()
##############################################################################
