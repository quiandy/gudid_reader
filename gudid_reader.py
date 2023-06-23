import urllib.request
from html.parser import HTMLParser
import csv
import sys

input_file = sys.argv[1]

class GUDIDParser(HTMLParser):
   device_number = ""
   brand_name = ""
   gmdn = ""

   parse_ids = False
   parse_description = False
   parse_gmdn = 0

   def handle_starttag(self, startTag, attrs):
      # Looking for the tag with the device_number and brand name
      if len(attrs)>0 and \
         attrs[0][0]=='href' and \
         "/devices/" in attrs[0][1] and \
         not "/devices/search" in attrs[0][1]: 
            self.parse_ids = True
      elif len(attrs)==1 and attrs[0][1] == "xsmall-12 medium-11 columns description":
            self.parse_description = True

   def handle_data(self, data):
       if self.parse_ids:
          self.brand_name = data.split('-')[0].strip()
          self.device_number = data.split('-')[1].strip()
          self.parse_ids = False
       elif self.parse_description:
          self.description = data.strip("\\t\\n")
          self.parse_description = False
       elif(data == "GMDN Term"):
            self.parse_gmdn = 6
       elif(self.parse_gmdn > 0):
           self.parse_gmdn -= 1;
           if self.parse_gmdn == 0:
               self.gmdn = data.strip("\\t\\n").replace("(1)","").strip()

base_url = 'https://accessgudid.nlm.nih.gov/devices/search?query='
#catalog_number = '187702735'

print("Catalog Number,Device Number,Brand Name,Description,GMDN")

with open(input_file) as csvfile:
   reader = csv.reader(csvfile, delimiter=',')
   header_row = True
   for row in reader:
      if header_row:
         header_row = False
      else:
         catalog_number = row[0]
         response = urllib.request.urlopen(base_url + catalog_number)
         parser = GUDIDParser()
         parser.feed(str(response.read()))
         parser.close()
   print(catalog_number + "," + parser.device_number + "," + parser.brand_name + "," + parser.description + "," + parser.gmdn)