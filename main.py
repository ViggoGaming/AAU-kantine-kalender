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

# Determine the start date as the date 14 days prior to today
start_date = datetime.today() - timedelta(days=14)

# Determine the end date as the date 14 days after today
end_date = datetime.today() + timedelta(days=14)

# Fetch the CISESSION cookie and update the headers
cisession_cookie_value = fetch_cisession_cookie()
headers = {'Cookie': f'cookiesDirective=1; CISESSION={cisession_cookie_value}'}
print(headers)

# Fixed time for the menu events (11:00-12:00 Danish time)
start_time = datetime.strptime('09:00 AM', '%I:%M %p')
end_time = datetime.strptime('10:00 AM', '%I:%M %p')

# Create a function to scrape and save the daily menu as a single event
def scrape_and_save_menu():
    cal = Calendar()
    cal.name = "Jespers Torvekøkken"

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%d-%m-%Y')
        url_template = f'https://aau.torvekoekken.dk/templates/menuliste/?date={date_str}&id=487'
        
        response = requests.get(url_template, headers=headers)
        print(response.text)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if "Menu endnu ikke planlagt" not in soup.text:

                menu_sections = {}
                current_section = None
                for child in soup.find_all(['div', 'span']):  # Assuming parent doesn't have a unique identifier, iterating through all divs
                    if child.name == 'div' and 'menu_header_ny' in child['class']:
                        current_section = child.text.strip() + ':'
                        menu_sections[current_section] = []
                    elif current_section and child.name == 'div' and 'menu_ret_ny' in child['class']:
                        menu_sections[current_section].append(child.text.strip())

                event_description = []
                for section, items in menu_sections.items():
                    event_description.append(section)
                    for index, item in enumerate(items, 1):
                        event_description.append(f" {item}")

                event_description = "\n".join(event_description)
                additional_description = "Udviklet af Victor Buch, (https://victorbuch.dk)"
                event_description += f"\n\n{additional_description}"

                if event_description:  # Check if there's a description to add
                    e = Event()
                    e.name = "Dagens menu🍽️"
                    e.description = event_description

                    event_start = datetime.combine(current_date, start_time.time())
                    event_end = datetime.combine(current_date, end_time.time())
                    e.begin = event_start
                    e.end = event_end

                    cal.events.add(e)
                    print("Created event for", current_date.strftime('%d-%m-%Y'))

            else:
                print("No menu available for", current_date.strftime('%d-%m-%Y'))

        current_date += timedelta(days=1)

    filename = "./files/kantine-kalender.ics"
    with open(filename, 'w') as ics_file:
        ics_content = str(cal)
        ics_content = ics_content.replace('END:VCALENDAR', 'X-WR-CALNAME:Jespers Torvekøkken kantine\nEND:VCALENDAR')
        ics_file.write(ics_content)

    print(f"ICS file generated from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')} as {filename}.")

scrape_and_save_menu()
