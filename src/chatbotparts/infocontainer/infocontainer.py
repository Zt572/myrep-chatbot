#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Feb 2022
# version ='1.0'
# Copyright Feb 2022
# ---------------------------------------------------------------------------
""" Create customizable information containers for handling the string of information they contain.
More specific container types are included for use in the District chatbot which have their
own unique keyword dictionaries."""
# ---------------------------------------------------------------------------
import collections
import re
# ---------------------------------------------------------------------------


class InfoContainer():
    """ A container for storing string data and searching it based on its keyword
    dictionary.
    """
    _data = None
    _keyword_dict = None

    def __init__(self, data, keyword_dict={}):
        """Creates a new InfoContainer with the given data.
        Non-string data results in error. Providing a keyword
        dictionary is optional; specialized InfoContainers provide
        their own dictionaries."""
        self.set_data(data)
        self.set_dict(keyword_dict)

    def get_raw_data(self):
        return self._data

    def set_data(self, data):
        if isinstance(data, str):
            self._data = data
        else:
            raise TypeError("Data in InfoContainer must be a string")

    def get_dict(self):
        return self._dict

    def set_dict(self, keyword_dict):
        """Sets the InfoContainer's dictionary of keywords to relevant info.
        Passing non-dictionary types results in error."""

        # If dict is a dictionary type, carry on
        if isinstance(keyword_dict, collections.Mapping):
            self._dict = keyword_dict
        else:
            raise TypeError("Dictionary in InfoContainer must be a valid dictionary type")

    def search(self, term):
        """Searches the container's data for the relevant
        search term. If the term is in the InfoContainer's
        keyword dictionary, the relevant data will be provided."""

        if isinstance(term, str):
             # Check to see if dictionary value is a string or object with EAFP principle (if the key exists)
            try:
                return self._dict[term.lower()].center(0)
            except AttributeError:  # If the key exists but the value can't handle .center(), it's not a string
                return self._dict[term.lower()].__str__()   # Return the object's summary string
            except KeyError:
                return "UNRETRIEVED"
        else:
            raise TypeError("Term must be a string")

    def format_dict_info(self):
        """Returns a formatted string of all the information 
        found in the container's dictionary."""

        output = ""
        for entry in self.get_dict():
            output += f"{entry.title()}: {self.get_dict()[entry]}\n"
        return output

# Classes for Contact Info

class _Address():
    street = None
    cityzip = None

    # Prints a string representation of the Address
    def __str__(self):
        output = ""
        if self.street is not None: output += self.street + ", "
        if self.cityzip is not None: output += self.cityzip + " "
        return output


class ContactInfoContainer(InfoContainer):
    """ Specialized Info Container for Contact Info."""

    _home_address = _Address()
    _columbia_address = _Address()
    _contact_info_dict = {
        "name": None,
        "home address": None,
        "columbia address": None,
        "phone": None
    }

    def __init__(self, data):
        super().__init__(data)              # Store the data
        self._build_contact_dictionary()    # Build relevant contact info dictionary values from supplied data

    def _build_contact_dictionary(self):
        try:
            # Since the Columbia address appears first in the html, it's possible
            # to determine which of the two results belongs to which address
            m = re.compile('(?<=\>)\d{1,3}[\w!\ ]{1,3}?\ [\w\ ]*')
            address_streets = m.findall(self.get_raw_data())
            m = re.compile('(?<=\>)[a-zA-Z-.\ ]+\ [0-9]{5}')
            address_cityzips = m.findall(self.get_raw_data())

            # Set address data
            self._columbia_address.street = address_streets[0]
            self._columbia_address.cityzip = address_cityzips[0]
            self._home_address.street = address_streets[1]
            self._home_address.cityzip = address_cityzips[1]
        except IndexError:  # If no results were found, just keep the entries as None
            pass

        # Update dictionary values
        try:
            m = re.compile('Representative\ [\w]+\ [\w].?\ [\w]+')                  # Name
            self._contact_info_dict['name'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass
        
        self._contact_info_dict['home address'] = self._home_address            # Addresses
        self._contact_info_dict['columbia address'] = self._columbia_address

        try:
            m = re.compile('(?<=>\ )\([0-9]{3}\)\ [0-9]{3}-[0-9]{4}')               # Phone
            self._contact_info_dict['phone'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass
        
        # Lastly, set this special dictionary to be the current dictionary
        self.set_dict(self._contact_info_dict)


# Classes for Personal Information

class _Education():
    _college_list = []

    # Prints a string representation of the Education
    def __str__(self):
        return "; ".join(self._college_list)


class PersonalInfoContainer(InfoContainer):
    """ Specialized Info Container for Personal Info."""

    _edu = _Education()
    _personal_info_dict = {
        "birthday": None,
        "parents": None,
        "education": None,
        "children": None,
        "former": None,
        "religion": None,
    }

    def __init__(self, data):
        super().__init__(data)              # Store the data
        self._build_personal_dictionary()    # Build relevant contact info dictionary values from supplied data

    def _build_personal_dictionary(self):
        # Find Education information, if available
        try:
            m = re.compile('[\w\ ]+,\ [\w.]+,\ [0-9]{4}')   # University, degree, year
            self._edu._college_list = []    # Clear college list to prevent repeated data on future calls
            for match in m.findall(self.get_raw_data()):
                self._edu._college_list.append(match)
        except IndexError:  # If no results were found, just keep the entries as None
            pass

        # Update dictionary values
        try:
            m = re.compile('Born\ [\w]+\ [0-9]{1,2}')                                     # Birthday
            self._personal_info_dict['birthday'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass
        
        try:
            m = re.compile('(?:Son|Daughter)\ [\w .,-]+')                               # Parents
            self._personal_info_dict['parents'] = m.findall(self.get_raw_data())[0] 
        except IndexError:  # If no results were found, keep entry as None
            pass
        
        self._personal_info_dict['education'] = self._edu                            # Education

        try:
            m = re.compile('[0-9]{0,2}\ child[\w]*,\ [\w.,\ -]*')                   # Children
            self._personal_info_dict['children'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass

        try:
            m = re.compile('Former[\w\ ,]*')                                        # Former jobs/roles
            self._personal_info_dict['former'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass

        try:
            m = re.compile('[\w\ .,-]*Church[\w\ .,-]*')                                        # Religion
            self._personal_info_dict['religion'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass
        
        # Lastly, set this special dictionary to be the current dictionary
        self.set_dict(self._personal_info_dict)


class ServiceInfoContainer(InfoContainer):
    """ Specialized Info Container for Service Info."""

    _service_info_dict = {
        "service":None
    }

    def __init__(self, data):
        super().__init__(data)              # Store the data
        self._build_service_dictionary()    # Build relevant contact info dictionary values from supplied data

    def _build_service_dictionary(self):
        # Find service info
        try:
            m = re.compile('(?<=list-style-type:square;\" >)[\w\ .,\'\"-]+')   # Service in public office
            self._service_info_dict['service'] = '\n'.join(m.findall(self.get_raw_data()))
        except:  # If an error occurs, just keep the entries as None
            pass

        # Lastly, set this special dictionary to be the current dictionary
        self.set_dict(self._service_info_dict)


class DistrictInfoContainer(InfoContainer):
    """ Specialized Info Container for District Info."""

    _district_info_dict = {
        "district name":None,
        "region":None
    }

    def __init__(self, data):
        super().__init__(data)              # Store the data
        self._build_district_dictionary()    # Build relevant contact info dictionary values from supplied data

    def _build_district_dictionary(self):
        # Find district info
        try:
            m = re.compile('District\ [0-9]+')                           # Number/Name
            self._district_info_dict['district name'] = m.findall(self.get_raw_data())[0]
        except IndexError:  # If no results were found, keep entry as None
            pass

        try:
            m = re.compile('(?<=x;">)(.*)Count[\w]{1,3}')                           # Region
            # Since &amp; is used for '&', replace it
            self._district_info_dict['region'] = m.findall(self.get_raw_data())[0].replace('&amp;','&') 
        except IndexError:  # If no results were found, keep entry as None
            pass

        # Lastly, set this special dictionary to be the current dictionary
        self.set_dict(self._district_info_dict)
