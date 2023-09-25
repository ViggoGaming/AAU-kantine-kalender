import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta

def fetch_cisession_cookie():
    url = 'https://aau.torvekoekken.dk'
    response = requests.get(url)
    
    # Fetch the CISESSION cookie value
    cisession_cookie = response.cookies.get('CISESSION')
    print(cisession_cookie)

    if not cisession_cookie:
        raise ValueError("Failed to fetch the CISESSION cookie!")
    
    return cisession_cookie



# Calculate the start date as September 1, 2023
start_date = datetime(2023, 9, 1)

# Calculate the end date as September 30, 2023
end_date = datetime(2023, 9, 30)

# Define the custom headers
headers = {}

# Fetch the CISESSION cookie and update the headers
cisession_cookie_value = fetch_cisession_cookie()
headers['Cookie'] = f'cookiesDirective=1; CISESSION={cisession_cookie_value}'

print(headers)

# Fixed time for the menu events (11:00-12:00 Danish time)
start_time = datetime.strptime('09:00 AM', '%I:%M %p')
end_time = datetime.strptime('10:00 AM', '%I:%M %p')

# Create a function to scrape and save the daily menu as a single event
def scrape_and_save_menu():
    # Create a new iCalendar (ICS) calendar
    cal = Calendar()

    cal.name = "Jespers Torvekøkken"

    # Iterate through all dates in September 2023
    current_date = start_date
    while current_date <= end_date:
        # Construct the URL for the specified date
        date_str = current_date.strftime('%d-%m-%Y')
        url_template = f'https://aau.torvekoekken.dk/templates/menuliste/?date={date_str}&id=487'
        # Send an HTTP GET request to the URL with custom headers
        response = requests.get(url_template, headers=headers)
        print(response.text)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Create a list to store menu items for the day
            menu_items_for_day = []

            # Iterate through the menu items
            menu_items = soup.find_all('div', class_='menu_ret_ny')
            for menu_item in menu_items:
                # Extract the menu item name
                menu_item_name = menu_item.text.strip()
                
                # Add the menu item to the list for the day
                menu_items_for_day.append(menu_item_name)

            # If there are menu items for the day, create an event
            if menu_items_for_day:
                # Create an ICS event
                e = Event()

                # Set the event title as "Dagens menu"
                e.name = "Dagens menu🍽️"

                # Combine menu items into the event description with prefixes
                event_description = "\n".join([f"Ret{menu_items_for_day.index(item) + 1}: {item}" for item in menu_items_for_day])
                e.description = event_description
                
                additional_description = "Udviklet af Victor Buch, (https://victorbuch.dk)"
                e.description += f"\n{additional_description}"

                # Set the event date to the specified date and fixed time
                event_start = datetime.combine(current_date, start_time.time())
                event_end = datetime.combine(current_date, end_time.time())
                e.begin = event_start
                e.end = event_end

                # Add the event to the calendar
                cal.events.add(e)
                print("Create event for", current_date.strftime('%d-%m-%Y'))

        # Move to the next date
        current_date += timedelta(days=1)

    # Save the calendar to an ICS file for the entire month
    filename = "./files/kantine-kalender.ics"
    with open(filename, 'w') as ics_file:
        ics_content = str(cal)
        ics_content = ics_content.replace('END:VCALENDAR', 'X-WR-CALNAME:Jespers Torvekøkken kantine\nEND:VCALENDAR')
        ics_file.write(ics_content)

    print(f"ICS file generated for the entire month of September 2023 as {filename}.")

# Call the function to generate the single menu event for the entire month
scrape_and_save_menu()
