from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from collections import ChainMap
from itertools import starmap

import os
import sys
import shelve


class FormFiller:

    def __init__(self, url, submit, *di_args, **kwargs):
        """
        Initializes a FormFiller instance, an object designed to automatically
        submit text to specified forms on a website.

        Parameters
        ----------
        url : string
            URL of the website.
        submit : string
            CSS selector of the relevant submission button. To force FormFiller
            to send an ENTER keypress instead (recommended), set this argument
            to None.
        *di_args : dictionary
            Zero or more dictionaries whose keys are CSS selectors for input
            fields and whose values are string to input. All values are coerced
            to string.
        **kwargs : 
           Zero or more key-value pairs of CSS selectors and input strings.
           Mutually compatible with di_args.

        Returns
        -------
        None.

        """
        self.url = url
        self.submit = submit
        self.selectors = {**dict(ChainMap(*di_args)), **kwargs}
        self.selectors = {k : str(v) for k, v in self.selectors.items()}
        self.submitted = False
        
    def __repr__(self):
        """
        If slectors contains 1 or more values, prints a formatted table with key-value
        pairs. If none are set, prints a notice saying so isntead. Either way,
        prints value of URL and submit selector

        Returns
        -------
        String reprsentation of the instance.

        """
        
        ident = f"A FormFiller object for url '{self.url}'"
        if self.selectors:
            
            sep = " | "
            maxes = zip(map(lambda x: len(sorted(x, key = len, reverse = True)[0]),
                            [self.selectors.keys(),
                             self.selectors.values()]),
                        map(len, ["CSS", "Values"]))
            widths = dict(zip(["key", "value"],
                              starmap(max, maxes)))
            headers = sep.join(["CSS".ljust(widths["key"]), "Value".ljust(widths["value"])])
            dashes = "-" * (sum(widths.values()) + len(sep))
            selectors = "\n".join([sep.join([str(k).ljust(widths["key"]),
                                             str(v).ljust(widths["value"])]) for k, v in self.selectors.items()])
            body = f"""Selectors:\n
{headers}
{dashes}
{selectors}\n"""
        else:
            body = "No selectors currently assigned to values\n"
        if self.submitted:
            status = "Submitted"
        else:
            status = "Not yet submitted"
        return f"""{ident}
{body}
Submit element: {self.submit}
{status}"""
        
    """Add new selectors, using the same interface as __init__"""
    def add(self, *di_args, **kwargs):
        new = {**dict(ChainMap(*di_args)), **kwargs}
        new = {k : v  for k, v in new.items() if k not in self.selectors.keys()}
            
        self.selectors = {**self.selectors, **new}
    
    """Remove all sepcified selectors from object"""
    def remove(self, *selectors):
        
        # See https://stackoverflow.com/questions/8995611/removing-multiple-keys-from-a-dictionary-safely/8995774#8995774
        #dict.pop's second arg is a default value
        for k in selectors:
            self.selectors.pop(k, None)
    
    """Reset all keys to None"""
    def clear(self):
        self.selectors = dict.fromkeys(self.selectors.keys(), None)
        self.submitted = False
        
    """Set existing keys to new values"""
    def update(self, *di_args, **kwargs):
        new = {**dict(ChainMap(*di_args)), **kwargs}
        new = {k :v for k, v in new.items() if k in self.selectors.keys()}
        self.selectors = {**self.selectors, **new}
        
    def execute(self, webdriver_path = None):
        """
        Performs the main action of the FormFiller class by entering and 
        submitting input text at the provided URL. After verifying the Webdriver
        executable and trying the URL, this method attempts to find each selected 
        input and send the corresponding text, informing the user of any
        failures. It then attempts to submit and exits.

        Parameters
        ----------
        webdriver_path : string, optional
            DESCRIPTION. Path to user's Webdriver executable.
            If the WEBDRIVER environment variable is not set, this
            argument must be supplied in order for the function to work.
            The default is None.

        Returns
        -------
        None.

        """
        if not webdriver_path:
            if not (webdriver_path := os.environ.get("WEBDRIVER")):
                print("Webdriver path not specified and WEBDRIVER environment variable does not exist")
                return
        browser = webdriver.Firefox(executable_path = webdriver_path)
                                    
        try:
            browser.get(self.url)
        except:
            print(f"Could not access {self.url}")   
            return
        #Only attempt to enter inputs with non-None values
        if not any(self.selectors.keys()):
            print("No input values initialized. Exiting.")
            return
        
        #Use of wait adapted from https://pythonbaba.com/python-code-to-press-enter-key-using-selenium/
        wait = WebDriverWait(browser, 10)
        for k, v in self.selectors.items():
            if v:
                try:
                    inpt = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, k)))
                    inpt.send_keys(v)
                except:
                    print(f"Failed to find input {k}")
                    pass
        if self.submit:
            try:
                browser.find_element_by_css_selector(self.submit).click()
                self.submitted = True
            except:
                print(f"Failed to find submit element {self.submit}. Attempting to send ENTER key")
        
        inpt.send_keys(Keys.ENTER)