
import os
import uuid
import hashlib
import requests
import base64
import xml.etree.ElementTree as ET

class ECL:

    def __init__(self, url, user, password):

        self._url = url
        self._password = password
        self._user = user

        self._to = 10 # timeout in seconds 


    def generate_salt(self):

        return 'salt=' + str(uuid.uuid4())

    def signature(self, arguments, data=''):

        string = arguments
        string += ':'
        string += self._password
        string += ':'
        string += data

        print('Signature string:', string)

        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()


    def search(self, category='Purity+Monitors', limit=2):

        url = self._url
        url += '/xml_search?'

        arguments = f'c={category}&'
        arguments += f'l={limit}&'
        arguments += self.generate_salt()

        # headers = {'content-type': 'text/xml'}

        headers = {
            'X-Signature-Method': 'md5',
            'X-User': self._user,
            'X-Signature': self.signature(arguments)
        }

        print(headers)

        print(url + arguments)

        r = requests.get(url + arguments, headers=headers, timeout=self._to)

        print(r.url)

        print(r.text)

    def get_entry(self, entry_id=2968):

        url = self._url
        url += '/xml_get?'

        arguments = f'e={2968}&'
        arguments += self.generate_salt()

        # headers = {'content-type': 'text/xml'}

        headers = {
            'X-Signature-Method': 'md5',
            'X-User': self._user,
            'X-Signature': self.signature(arguments)
        }

        print(headers)

        print(url + arguments)

        r = requests.get(url + arguments, headers=headers, timeout=self._to)

        print(r.url)

        print(r.text)


    def post(self, entry, do_post=False):

        entry.set_author(self._user)

        xml_data = entry.show()#.strip()
        print('->', type(xml_data))

        url = self._url
        url += '/xml_post?'

        arguments = self.generate_salt()

        # headers = {'content-type': 'text/xml'}

        headers = {
            'content-type': 'text/xml',
            'X-Signature-Method': 'md5',
            'X-User': self._user,
            'X-Signature': self.signature(arguments, xml_data)
        }

        print(headers)

        print(url + arguments)

        if do_post:
            r = requests.post(url + arguments, headers=headers, data=xml_data, timeout=self._to)

            print(r.url)

            print(r.text)



class ECLEntry:

    def __init__(self, category, tags=[], formname='default', text='', preformatted=False,
                private=False, related_entry=None):

        self._category = category
        self._tags = tags
        self._formname = formname
        self._text = text

        # Create the top level element
        self._entry = ET.Element('entry', category=category)

        if not preformatted:
            self._entry.attrib['formatted']='formatted'

        if private:
            self._entry.attrib['private'] = 'yes'

        if related_entry:
            self._entry.attrib['related'] = str(related_entry)


        # Create the form
        self._form = ET.SubElement(self._entry, 'form', name=formname)
        if text:
            # Create the text field
            textfield = ET.SubElement(self._form, 'field', name='text')
            # Store the text
            textfield.text = text
        for tag in tags:
            ET.SubElement(self._entry, 'tag', name=tag)

    def set_value(self, name, value):
        
        field = ET.SubElement(self._form, 'field', name=name)
        field.text = value

    def set_author(self, name):
        self._entry.attrib['author'] = name

    def add_attachment(self, name, filename, data=None):
        
        field = ET.SubElement(self._entry, 'attachment', type='file', name=name, filename=os.path.basename(filename))
        
        if data:
            field.text = base64.b64encode(data)
        else:
            f = open(filename,'r')
            b = f.read()
            field.text = base64.b64encode(b)
            f.close()

    def add_image(self, name, filename, image=None):
        
        field = ET.SubElement(self._entry, 'attachment', type='image', name=name, filename=os.path.basename(filename))
        
        if image:
            field.text = base64.b64encode(image)
        else:
            with open(filename, 'rb') as image_file:
                base64_bytes = base64.b64encode(image_file.read())
                field.text = base64_bytes
                                
    def show(self):
        return str(ET.tostring(self._entry))



if __name__ == "__main__":

    print('Testing')

    ecl = ECL(url='https://dbweb9.fnal.gov:8443/ECL/sbnd/E', user='sbndprm', password='purityND!')

    # ecl.get_entry()
    # ecl.search()

    entry = ECLEntry(category='Purity Monitors', text='Example text')
    entry.set_author('sbndprm')
    # entry.add_image(name='prm', filename='/home/nfs/sbndprm/purity_monitor_data/sbnd_prm2_run_967_data_20240306-040135_ana.png')
    print(entry.show())
    print(entry.show().strip())

    ecl.post(entry)

