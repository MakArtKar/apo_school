import gspread
from PIL import Image
import gspread_formatting as gf
from random import randint
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint


def i2s(y):
    string = ""
    while y > 0:
        y, remainder = divmod(y - 1, 26)
        string = chr(65 + remainder) + string
    return string


def c2s(x, y):
    string = ""
    while y > 0:
        y, remainder = divmod(y - 1, 26)
        string = chr(65 + remainder) + string
    return string + str(x)


width = 100
height = 100

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("tutorial")

ws = sheet.worksheet('Picture')

im = Image.open("pic.png").convert('RGB')

gf.set_row_height(ws, '1:' + str(height), 10)
gf.set_column_width(ws, 'A:' + i2s(width), 10)

formats = []

h_scale = im.height // height
w_scale = im.width // width

for i in range(height):
    for j in range(width):
        r_s, g_s, b_s = 0, 0, 0
        cnt = 0

        for x in range(i * h_scale, (i + 1) * h_scale):
            for y in range(j * w_scale, (j + 1) * w_scale):
                r, g, b = im.getpixel((x, y))
                r_s += r

                g_s += g
                b_s += b
                cnt += 1

        cnt *= 255

        fmt = gf.CellFormat(backgroundColor=gf.Color(r_s / cnt, g_s / cnt, b_s / cnt))
        formats.append((c2s(j + 1, i + 1) + ':' + c2s(j + 1, i + 1), fmt))

gf.format_cell_ranges(ws, formats)