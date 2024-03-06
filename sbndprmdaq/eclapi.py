'''
Contains code to talk to the ECL API
'''
import os
import uuid
import hashlib
import base64
import xml.etree.ElementTree as ET
import requests

class ECL:
    '''
    The main ECL class that handles the connection with the ECL
    '''

    #pylint: disable=invalid-name

    def __init__(self, url, user, password):
        '''
        Contructor

        Args:
            url (str): the URL
            user (str): the username
            password (str): the password
        '''

        self._url = url
        self._password = password
        self._user = user

        self._to = 10 # timeout in seconds


    def generate_salt(self):
        '''
        Generates the salt random string
        '''

        return 'salt=' + str(uuid.uuid4())

    def signature(self, arguments, data=''):
        '''
        Constructs the signature, which is made with the arguments to pass to
        the API, the password, and the data (is POST) separated by ":". And the
        encoded.
        '''

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
        '''
        Searched the last entries in a given category

        Args:
            category (str): the category to search in
            limit (int): limit to the number of entries
        '''

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
        '''
        Gets a particular entry.

        Args:
            entry_id (int): The ID of the entry 
        '''

        url = self._url
        url += '/xml_get?'

        arguments = f'e={entry_id}&'
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
        '''
        Posts an entry to the e-log

        Args:
            entry (ECLEntry): the entry
            do_post (bool): set this to True to submit the entry to the ECL
        '''

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
    '''
    A class representing a single ECL entry
    '''
    #pylint: disable=invalid-name,too-many-arguments

    def __init__(self, category, tags=(), formname='default', text='', preformatted=False,
                private=False, related_entry=None):

        '''
        Contructor
        '''

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
        '''
        Sets a single value to the entry form
        '''

        field = ET.SubElement(self._form, 'field', name=name)
        field.text = value

    def set_author(self, name):
        '''
        Sets the author
        '''
        self._entry.attrib['author'] = name

    def add_attachment(self, name, filename, data=None):
        '''
        Adds a generic file attachment 
        '''

        field = ET.SubElement(self._entry, 'attachment', type='file', name=name, filename=os.path.basename(filename))

        if data:
            field.text = base64.b64encode(data)
        else:
            with open(filename, 'rb', encoding="utf-8") as file:
                base64_bytes = base64.b64encode(file.read())
                field.text = base64_bytes


    def add_image(self, name, filename, image=None, caption=''):
        '''
        Adds an image attachment
        '''

        field = ET.SubElement(self._entry, 'attachment', type='image', name=name, filename=os.path.basename(filename), caption=caption)

        if image:
            field.text = base64.b64encode(image)
        else:
            with open(filename, 'rb', encoding="utf-8") as image_file:
                base64_bytes = base64.b64encode(image_file.read())
                field.text = base64_bytes

    def show(self):
        '''
        Returns the entry in str format
        '''
        return str(ET.tostring(self._entry))



if __name__ == "__main__":

    print('Testing')

    PASSWD = ''
    ecl = ECL(url='https://dbweb9.fnal.gov:8443/ECL/sbnd/E', user='sbndprm', password=PASSWD)

    # ecl.get_entry()
    # ecl.search()

    entry_ = ECLEntry(category='Purity Monitors', text='Example text')
    entry_.set_author('sbndprm')
    # entry.add_image(name='prm', filename='/home/nfs/sbndprm/purity_monitor_data/sbnd_prm2_run_967_data_20240306-040135_ana.png')
    print(entry_.show())
    print(entry_.show().strip())

    ecl.post(entry_)
