import sqlite3
import pandas as pd

def fetch_data():
    # Connect to the database
    connection = sqlite3.connect('listings.db')
    cursor = connection.cursor()

    # Select all records from the table
    cursor.execute("SELECT * FROM listings")
    rows = cursor.fetchall()

    # Get headers
    headers = [description[0] for description in cursor.description]

    # Convert the data into a pandas dataframe
    data_frame = pd.DataFrame(rows, columns=headers)

    # Close the database connection
    connection.close()
    
    return data_frame

def generate_html_table(data_frame):
    # Convert the url column to HTML anchor tags
    data_frame['url'] = data_frame['url'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')

    # Convert the dataframe to an HTML table
    html_table = data_frame.to_html(escape=False, index=False)

    # Generate the page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Listings Table</title>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            table, th, td {{
                border: 1px solid black;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h2>Listings</h2>
        {html_table}
    </body>
    </html>
    """
    
    # Write the HTML content to a file
    with open('listings_table.html', 'w') as file:
        file.write(html_content)

def main():
    # Retrieve data from the database
    data_frame = fetch_data()

    # Generate the table
    generate_html_table(data_frame)
    print("The table has been saved as 'listings_table.html'.")

if __name__ == '__main__':
    main()
