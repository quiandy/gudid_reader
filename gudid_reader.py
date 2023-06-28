import argparse
import multiprocessing
import urllib.request
import html.parser
import csv

argparser = argparse.ArgumentParser(prog='gudid reader',
                                          description='Python script calling the accessgudid website to obtain info on a given catalogue number')

argparser.add_argument("-i", "--input", required=True, help="csv file containing in the first columns the catalogue numbers to search")
argparser.add_argument("-o", "--output", default="output.csv", help="csv file in which to dump outputs")
args = argparser.parse_args()

class GUDIDParser(html.parser.HTMLParser):
   device_number = "NOT FOUND"
   brand_name = "NOT FOUND"
   description = "NOT FOUND"
   gmdn = "NOT FOUND"

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
catalog_number_list = None

def getData(catalog_number):
   response = urllib.request.urlopen(base_url + catalog_number)
   parser = GUDIDParser()
   parser.feed(str(response.read()))
   parser.close()
   return [catalog_number, parser.device_number, parser.brand_name, parser.description, parser.gmdn]

if __name__ == '__main__':

   #catalog_number = '187702735'
   with open(args.input) as csv_input:
      
      reader = csv.reader(csv_input, delimiter=',')
      catalog_number_list = [row[0] for row in reader]
      #remove first element (haeader)
      catalog_number_list.pop(0)
      
   total_catalog_numbers = len(catalog_number_list)
   print("Found {0} rows to fill, starting...".format(total_catalog_numbers ))

   with open(args.output, 'w') as csv_output:
      
      writer = csv.writer(csv_output)
      header = ['Catalog Number','Device Number','Brand Name','Description','GMDN']
      writer.writerow(header)
      completed_items = 0

      with multiprocessing.Pool() as pool:
         for result in pool.imap(getData, catalog_number_list):
            completed_items = completed_items + 1         
            writer.writerow(result)
            print("Completed {0} items, {1} more to go".format(completed_items, total_catalog_numbers - completed_items))
