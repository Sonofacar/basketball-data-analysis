# Imports
import re
import pandas

pandas.options.mode.copy_on_write = True

# scraping library
import lib.get_page
from lib.utility_functions import *


# Other Variables
base_url = 'https://www.basketball-reference.com'
db_name = '../bball_db'
page = lib.get_page.page()


# Main script
