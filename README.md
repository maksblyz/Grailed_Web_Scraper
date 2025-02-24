# Grailed_Web_Scraper

This project involves a Python-based web scraper designed to find clothing listings that match specific measurements from Grailed.com. The scraper utilizes Selenium for web interactions, stores the data in an SQLite database, processes and organizes it using Pandas, and displays the results in dynamically generated HTML tables for easy web viewing.

# To Run the Program:

1. Execute main_scraper.py and respond to the prompts in the terminal.
2. Run table_generator.py to generate the HTML file.

You will then have an HTML file to easily view the results.

# Files:

main_scraper.py: Contains the Python code for the web scraper using Selenium. This script handles the extraction of clothing listings based on predefined criteria and sends the data to a SQLite database.

website_generator.py: Uses Pandas to process the data stored in SQLite and generates HTML tables that are structured to provide an easily navigable and clean user interface.

# Requirements:

Python 3.x

Libraries: Selenium, Pandas, SQLite3,

Web Browser (for viewing the HTML output)
