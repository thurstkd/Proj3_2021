import sqlite3
import plotly
import plotly.graph_objects as go 

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands
def process_command(command):
    """
    command: string
    returns: a list of tuples. records matching query, including relevant fields.
High level commands
All commands must begin with one of the high level commands as the first term.

    """

    if command.split()[0]=="bars":
        query = bars_command(command)
    elif command.split()[0]=="companies":
        query = companies_command(command)
    elif command.split()[0]=="countries":
        query = countries_command(command)
    elif command.split()[0]=="regions":
        query = regions_command(command)

    connection = sqlite3.connect("choc.sqlite")
    cursor = connection.cursor()
    drop_results = '''
        DROP TABLE IF EXISTS "Results";
    '''

    cursor.execute(drop_results)
    result = cursor.execute(query).fetchall()
    table_query = "CREATE TABLE IF NOT EXISTS Results as "+query
    cursor.execute(table_query)

    connection.commit()
#    connection.close()
    if command.split()[-1]=="barplot":
        graph_results(command, result) 

    drop_results = '''
        DROP TABLE IF EXISTS "Results";
    '''

    #cursor.execute(drop_results)
    #connection.close()
    print(result)
    return result



def bars_command(command): 
    """
    Lists chocolate bars, according to the specified parameters.
    Valid options: none, country, region, sell, source, ratings, cocoa, top, bottom, <integer>
    Returns an SQL-formatted command(str)
    """
    bar_query = "SELECT SpecificBeanBarName, Company, Countries.EnglishName, Rating, CocoaPercent, BroadBeanOriginId FROM Bars "
    if "source" in command: 
        bar_query = bar_query + "JOIN Countries ON Countries.Id=Bars.BroadBeanOriginId "
        if "country":
            bar_query = bar_query + "WHERE Alpha2=" + "'"+command.split("country=")[-1][0:2]+"' "
        elif "region":
            bar_query = bar_query + "WHERE Region="+ "'"+command.split("region=")[-1].split()[0]+ "' "
    elif "sell" in command:
        bar_query = bar_query + "JOIN Countries ON Countries.Id=Bars.CompanyLocationId "
        if "country":
            bar_query = bar_query + "WHERE Alpha2="+ "'"+command.split("country=")[-1][0:2]+"' "
        elif "region":
            bar_query = bar_query + "WHERE Region="+ "'"+command.split("region=")[-1].split()[0]+ "' "
    else:
        bar_query = bar_query + "JOIN Countries ON Countries.Id=Bars.CompanyLocationId "

    bar_query = bar_query + "ORDER BY Rating DESC LIMIT 10 "

    if "cocoa" in command: 
        bar_query.replace("Rating", "CocoaPercent")

    if "bottom" in command: 
        bar_query = bar_query.replace("DESC", "ASC")
    
    for word in command.split():
        if word.isnumeric():
            bar_query = bar_query.replace("10", word)
    return bar_query

def companies_command(command): 
    """
    Lists chocolate bars sellers according to the specified parameters. Only companies that sell more than 4 bars are listed in results.
    Valid options: none, country, region, ratings, cocoa, number_of_bars, top, bottom, <integer>
    Returns an SQL-formatted command (str)
    """

    company_query = "SELECT Company, Countries.EnglishName, Rating FROM Bars JOIN Countries ON Countries.Id=Bars.CompanyLocationId "
    if "country" in command:
        company_query = company_query + "WHERE Alpha2=" + "'" + command.split("country=")[-1][0:2]+"' "
    elif "region" in command:
        company_query = company_query + "WHERE Region="+ "'"+command.split("region=")[-1].split()[0]+ "' "

    company_query = company_query + "ORDER BY Rating DESC LIMIT 10 "

    company_query = sorters(command, company_query)

    if "bottom" in command: 
        company_query = company_query.replace("DESC", "ASC")
    
    for word in command.split():
        if word.isnumeric():
            company_query = company_query.replace("10", word)

    return company_query

def sorters(command, query): 
    if "number_of_bars" in command:
        query = query.replace("Rating", "COUNT(Id) FROM Bars GROUP BY Company")
    elif "cocoa" in command:
        query = query.replace("Rating", "CocoaPercent")
    return query


def countries_command(command): 
    """
    Lists chocolate bars, according to the specified parameters.
    Valid options: none, country, region, sell, source, ratings, cocoa, number_of_bars, top, bottom, <integer>
    Returns an SQL-formatted command
    """
    if "source" in command: 
        country_query = "SELECT Countries.EnglishName, Countries.Region, Rating FROM Bars JOIN Countries ON Countries.Id=Bars.BroadBeanOriginId "
        if "region" in command:
            country_query = country_query + "WHERE Region="+ "'"+command.split("region=")[-1].split()[0]+ "' "

    elif "sell" in command:
        country_query = "SELECT Countries.EnglishName, Countries.Region, Rating FROM Bars JOIN Countries ON Countries.Id=Bars.CompanyLocationId "
        if "region" in command:
            country_query = country_query + "WHERE Region="+ "'"+command.split("region=")[-1].split()[0]+ "' "

    else:
        country_query = "SELECT Countries.EnglishName, Countries.Region FROM Bars JOIN Countries ON Countries.Id=Bars.CompanyLocationId "

    country_query = country_query + "ORDER BY Rating DESC LIMIT 10 "

    country_query = sorters(command, country_query)

    if "bottom" in command: 
        country_query = country_query.replace("DESC", "ASC")
    
    for word in command.split():
        if word.isnumeric():
            country_query = country_query.replace("10", word)

    return country_query

def regions_command(command): 
    """
    Lists chocolate bars, according to the specified parameters.
    Valid options: none, country, region, sell, source, ratings, cocoa, number_of_bars, top, bottom, <integer>
    Returns an SQL-formatted command
    """
    region_query = "SELECT Countries.Region, Rating FROM Bars "
    if "source" in command: 
        region_query = region_query + "JOIN Countries ON Countries.Id=Bars.BroadBeanOriginId "
    elif "sell" in command:
        region_query = region_query + "JOIN Countries ON Countries.Id=Bars.CompanyLocationId "

    region_query = region_query + "ORDER BY Rating DESC LIMIT 10 "

    region_query = sorters(command, region_query)

    if "bottom" in command: 
        region_query = region_query.replace("DESC", "ASC")
    
    for word in command.split():
        if word.isnumeric():
            region_query = region_query.replace("10", word)

    return region_query


def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue
        elif response.split()[0] =="bars" or response.split()[0] =="companies" or response.split()[0] =="countries" or response.split()[0] =="regions":
            process_command(response)
            continue
        else:
            print("Please refer to the documentation and enter a valid command. ")
            continue


def graph_results(command, query_result): 
    if command.split()[0]=="bars":
        bars = []
        sorter = []
        for bar in query_result:
            bars.append(bar[0])
            sorter.append(bar[3])

        bar_data = go.Bar(x=bars, y=sorter)
        basic_layout = go.Layout(title="Chocolate Bars")
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()

    elif command.split()[0]=="companies":
        companies = []
        sorter = []
        for company in query_result:
            companies.append(company[0])
            sorter.append(company[2])

        bar_data = go.Bar(x=companies, y=sorter)
        basic_layout = go.Layout(title="Chocolate Makers")
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()

    elif command.split()[0]=="countries":
        """
        x-axis: Country Name
y-axis: ratings/cocoa percentage/number_of_bars (whichever was specified)
        """
        countries = []
        sorter = []
        for country in query_result:
            countries.append(country[0])
            sorter.append(country[2])

        bar_data = go.Bar(x=countries, y=sorter)
        basic_layout = go.Layout(title="Chocolate Countries")
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()

    elif command.split()[0]=="regions":
        """
        """
        regions = []
        sorter = []
        for region in query_result:
            regions.append(region[0])
            sorter.append(region[1])

        bar_data = go.Bar(x=regions, y=sorter)
        basic_layout = go.Layout(title="Chocolate Regions")
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()


# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()
