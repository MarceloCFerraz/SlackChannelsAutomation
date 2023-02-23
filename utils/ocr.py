import cv2
import numpy as np
from PIL import ImageGrab
from src import image_treatment, image_capture
from src import common
import pytesseract as tesseract
from pytesseract import Output
import numpy as nm
import cv2
import re


def extractText(captura):
    # Converted the image to monochrome for it to be easily
    # read by the OCR and obtained the output String.
    texto = tesseract.image_to_string(cv2.cvtColor(nm.array(captura), cv2.COLOR_BGR2GRAY), lang='por+eng')
    texto = texto.split('\n')

    textofinal = ""

    for linha in texto:
        if not linha.isspace() and len(linha) > 0:
            textofinal += linha

    return (textofinal)


def extractTextRgb(captura):
    # Converted the image to monochrome for it to be easily
    # read by the OCR and obtained the output String.
    texto = tesseract.image_to_string(captura, lang='por+eng')
    texto = texto.split('\n')

    textofinal = ""

    for linha in texto:
        if not linha.isspace() and len(linha) > 0:
            textofinal += linha

    return (textofinal)


def extractTextBgr(captura):
    # Converted the image to monochrome for it to be easily
    # read by the OCR and obtained the output String.
    texto = tesseract.image_to_string(captura, lang='por+eng')
    texto = texto.split('\n')

    textofinal = ""

    for linha in texto:
        if not linha.isspace() and len(linha) > 0:
            textofinal += linha

    return (textofinal)


def verifyLogin(popupLogin):
    texto = extractText(
        image_capture.printScreen(popupLogin[0],
                                  popupLogin[1],
                                  popupLogin[2],
                                  popupLogin[3]
                                  )
    )
    return "Fazer Login" in texto


def verifyInRoulette(roulette):
    x = 0
    y = 0
    w = 0
    h = 0
    achoulocal = False

    texto = roulette.split(" ")

    print = image_capture.printScreen(14, 263, 521, 528)
    gray = image_treatment.imgToGray(print)
    limiar = image_treatment.otsuLimiarization(gray)
    # inverter as cores
    limiar = 255 - limiar

    dict = extractDict(limiar)
    x, y, w, h, limiar, achoulocal = findTextOnImg(dict, limiar, texto)

    return achoulocal


def verifyInactivity():
    texto = extractText(image_capture.printScreen(583, 549, 813, 585))

    return "inatividade" in texto


def verifyDisconnection():
    texto = extractText(image_capture.printScreen(557, 548, 804, 585))

    return "desligado" in texto


def findTextOnImg(dict, img, texto):
    achou = False
    for i in range(0, len(dict["text"])):
        reliability = int(float(dict["conf"][i]))
        x = dict["left"][i]
        y = dict["top"][i]
        w = dict["width"][i]
        h = dict["height"][i]
        text = dict["text"][i]

        if reliability > 20:
            cv2.rectangle(img,
                          (x, y),
                          (x + w, y + h),
                          (0, 0, 0),
                          1)
            # cv2.rectangle(img_copia,
            #               (x, y),
            #               (x+w, y+h),
            #               (255,255,255),
            #               1)

        if texto[0].upper() in text.upper() and not achou:
            if len(texto) > 1:
                if (texto[1].upper() in text.upper()) or (texto[1].upper() in dict["text"][i + 1].upper()):
                    achou = True

                    # print("{0} - {1} ({2}, {3}, {4}, {5})".format(text + " " + dict["text"][i + 1],
                    #                                               confiabilidade,
                    #                                               x,
                    #                                               y,
                    #                                               x + w,
                    #                                               y + h)
                    #       )
            else:
                achou = True

                # print("{0} - {1} ({2}, {3}, {4}, {5})".format(text,
                #                                               confiabilidade,
                #                                               x,
                #                                               y,
                #                                               x + w,
                #                                               y + h)
                #       )
    return x, y, w, h, img, achou


def extractDict(rgb):
    dict = tesseract.image_to_data(rgb, output_type=Output.DICT)
    return dict


def analyseTelegram(img):
    retorno = ""
    achou = False
    dict = extractDict(img)

    while not achou:
        for i in range(1, 8):
            if i == 1:
                texto = ["GREN", "RESPEITA"]
                x, y, w, h, img, achou = findTextOnImg(dict, img, texto)
                retorno = "G"
            elif i == 2 and not achou:
                texto = ["RED", "NEM"]
                x, y, w, h, img, achou = findTextOnImg(dict, img, texto)
                retorno = "R"
            elif i == 3 and not achou:
                texto = ["MESA", "EM"]
                x, y, w, h, img, achou = findTextOnImg(dict, img, texto)
                retorno = "A"
            elif i == 4 and not achou:
                texto = ["JOGADA", "CONFIRMADA"]
                x, y, w, h, img, achou = findTextOnImg(dict, img, texto)
                retorno = "C"
            elif i == 5 and not achou:
                texto = ["MANIPULA"]
                x, y, w, h, img, achou = findTextOnImg(dict, img, texto)
                retorno = "M"
            elif i == 6 and not achou:
                texto = ["TURBULENTO"]
                x, y, w, h, img, achou = findTextOnImg(dict, img, texto)
                retorno = "T"
            elif not achou:
                retorno = "O"
                achou = True

    return retorno, img


def extractHour(img):
    dict = extractDict(img)
    datetime_pattern = "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    hora = ""

    for i in range(0, len(dict["text"])):
        confiabilidade = int(float(dict["conf"][i]))
        if confiabilidade > 20:
            texto = dict["text"][i]
            if re.match(datetime_pattern, texto):
                x = dict["left"][i]
                y = dict["top"][i]
                w = dict["width"][i]
                h = dict["height"][i]
                cv2.rectangle(img,
                              (x, y),
                              (x + w, y + h),
                              (0, 0, 0),
                              1)
                hora = texto
    return hora


def extractAnalysisRoulette(img):
    dict = extractDict(img)
    roulette = ""
    contador = 0
    achou = False

    for i in range(0, len(dict["text"])):
        confiabilidade = int(float(dict["conf"][i]))
        if confiabilidade > 40:
            if contador == 0:
                roulette += dict["text"][i] + " "
                contador += 1
            elif contador == 1:
                roulette += dict["text"][i]
                contador += 1
    for texto in common.roletas:
        if roulette.upper() in texto.upper():
            achou = True

    return roulette, achou


def verifyTelegramInput(x1, y1, x2, y2):
    achou = False
    entradas_validas = ["pares",
                        "impares",
                        "ímpares",
                        "coluna",
                        "colunas",
                        "dúzia",
                        "duzia"]

    while not achou:
        texto = extractTextBgr(
            image_treatment.rawImgOtsuLimiarization(
                image_capture.printScreen(x1, y1, x2, y2)
            )
        )

        for entrada in entradas_validas:
            if entrada.upper() in texto.upper():
                achou = True

    return texto


def printWholeScreen(x, y):
    # ImageGrab-To capture the screen image in a loop.
    # Bbox used to capture a specific area.
    return ImageGrab.grab(bbox=(0, 0, x, y))


def printScreen(x1, y1, x2, y2):
    # ImageGrab-To capture the screen image in a loop.
    # Bbox used to capture a specific area.
    return ImageGrab.grab(bbox=(x1, y1, x2, y2))


def drawRectangleImg(img):
    dict = image_analysis.extractDict(img)

    for i in range(0, len(dict["text"])):
        confiabilidade = int(float(dict["conf"][i]))
        x = dict["left"][i]
        y = dict["top"][i]
        w = dict["width"][i]
        h = dict["height"][i]
        # if confiabilidade > -2:
        cv2.rectangle(img,
                      (x, y),
                      (x + w, y + h),
                      (255, 255, 255),
                      1)
        # cv2.rectangle(img_copia,
        #               (x, y),
        #               (x+w, y+h),
        #               (255,255,255),
            #
    return img


def drawRectangleCoordinates(img, x, y, w, h):
    cv2.rectangle(img,
                  (x, y),
                  (x + w, y + h),
                  (0, 0, 0),
                  1)
    # cv2.rectangle(img_copia,
    #               (x, y),
    #               (x+w, y+h),
    #               (255,255,255),
    #
    return img


def showImage(img):
    cv2.imshow("", img)
    cv2.waitKey()


def medianBlur(img):
    return cv2.medianBlur(img, 3)


def bilateralBlur(img):
    return cv2.bilateralFilter(img, 15, 55, 45)


def erodeImg(img):
    return cv2.erode(img, np.ones((3, 3), np.uint8))


def dilateImg(img):
    return cv2.dilate(img, np.ones((3, 3), np.uint8))


def openingImg(img):
    erosao = erodeImg(img)
    return cv2.dilate(erosao, np.ones((5, 5), np.uint8))


def closingImg(img):
    dilatar = dilateImg(img)
    return cv2.erode(dilatar, np.ones((5, 5), np.uint8))


def expandImg(img, fator_de_ampliação):
    # cv2.INTER_NEAREST (vizinho mais próximo. mais rápido)
    # cv2.INTER_LINEAR (bilinear. padrão. boa para aumentar ou diminuir)
    # cv2.INTER_AREA (melhor para redução. para ampliar, é semelhante ao nearest)
    # cv2.INTER_CUBIC (2ª melhor para ampliação. matriz 4x4 de pixels vizinhos
    # cv2.INTER_LANCZOS4 (melhor para ampliação. matriz 8x8 pixels vizinhos
    return cv2.resize(img, None, fx=fator_de_ampliação, fy=fator_de_ampliação, interpolation=cv2.INTER_CUBIC)


def invertImg(img):
    return 255 - img


def rawImgOtsuLimiarization(img):
    img = otsuLimiarization(imgToGray(imgToRgb(img)))
    return img


def basicLimiarization(gray):
    limiar, img = cv2.threshold(gray, 195, 255, cv2.THRESH_BINARY)
    # print("- Limiar atual: {}".format(limiar))
    # cv2.imshow("Limiarizacao Simples", limiar)
    # cv2.waitKey()

    return img


def resultsLimiarization(gray, limiar):
    limiar, img = cv2.threshold(gray, limiar, 255, cv2.THRESH_BINARY)
    # print("- Limiar atual: {}".format(limiar))
    # cv2.imshow("Limiarizacao Simples", limiar)
    # cv2.waitKey()

    return img


def otsuLimiarization(gray):
    limiar, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # print("- Limiar Gaussiano: {}".format(limiar))
    # cv2.imshow("Limiarizacao Simples", limiar)
    # cv2.waitKey()

    return img


def mediumAdaptLimiarization(gray):
    img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 9)
    # cv2.imshow("Limiarizacao Simples", limiar)
    # cv2.waitKey()

    return img


def gaussAdaptLimiarization(gray):
    img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 7)
    # cv2.imshow("Limiarizacao Simples", limiar)
    # cv2.waitKey()

    return img


def imgToRgb(img):
    rgb = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    return rgb


def imgToGray(img):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    return gray


def bgrToGray(bgr):
    gray = cv2.cvtColor(np.array(bgr), cv2.COLOR_BGR2GRAY)
    return gray

