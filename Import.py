import sqlite3
import sys
import xml.etree.ElementTree as ET

# Incoming Pokemon MUST be in this format
#
# <pokemon pokedex="" classification="" generation="">
#     <name>...</name>
#     <hp>...</name>
#     <type>...</type>
#     <type>...</type>
#     <attack>...</attack>
#     <defense>...</defense>
#     <speed>...</speed>
#     <sp_attack>...</sp_attack>
#     <sp_defense>...</sp_defense>
#     <height><m>...</m></height>
#     <weight><kg>...</kg></weight>
#     <abilities>
#         <ability />
#     </abilities>
# </pokemon>



# Read pokemon XML file name from command-line
# (Currently this code does nothing; your job is to fix that!)
if len(sys.argv) < 2:
    print("You must pass at least one XML file name containing Pokemon to insert")

#Connect to SQlite database
connection = sqlite3.connect("pokemon.sqlite")
cursor = connection.cursor()


for i, arg in enumerate(sys.argv):
    # Skip if this is the Python filename (argv[0])
    if i == 0:
        continue
    
    #parse XML doc
    xml_file = arg
    tree = ET.parse(xml_file)
    root = tree.getroot()

    #Extract the deets
    pokemon_data = {}

    pokemon_data["pokedex_number"] = root.attrib.get("pokedexNumber", "")
    pokemon_data["classification"] = root.attrib.get("classification", "")
    pokemon_data["generation"] = root.attrib.get("generation", "")

    pokemon_data["name"] = root.findtext("name", "")
    pokemon_data["hp"] = root.findtext("hp", "")
    pokemon_data["types"] = [type_element.text for type_element in root.findall("type")]
    pokemon_data["attack"] = root.findtext("attack", "")
    pokemon_data["defense"] = root.findtext("defense", "")
    pokemon_data["speed"] = root.findtext("speed", "")
    pokemon_data["sp_attack"] = root.findtext("sp_attack", "")
    pokemon_data["sp_defense"] = root.findtext("sp_defense", "")
    pokemon_data["height_m"] = root.findtext("height/m", "")
    pokemon_data["weight_kg"] = root.findtext("weight/kg", "")
    pokemon_data["abilities"] = [ability_element.text for ability_element in root.findall("abilities/ability")]

    # Check if classification already exists in the classification table
    cursor.execute("SELECT id FROM classification WHERE text=?", (pokemon_data["classification"], ))
    existing_classification = cursor.fetchone()

    if existing_classification is None:
        # Classification does not exist, insert it into the classification table
        cursor.execute("INSERT INTO classification (text) VALUES (?)", (pokemon_data["classification"], ))
        connection.commit()
        classification_id = cursor.lastrowid
    else:
        # Classification already exists, use its ID
        classification_id = existing_classification[0]






    #Make sure that pokemon does not already exist in db
    cursor.execute("SELECT COUNT(*) FROM pokemon WHERE name=?", (pokemon_data["name"], ))
    found_pokemon = cursor.fetchone()[0]

    if found_pokemon > 0:
        print("Sorry but that pokemon already exists in the database")
        continue

    #pokemon is not a duplicate, now I can put it into the database
    cursor.execute("""
        INSERT INTO pokemon (pokedex_number, classification_id, generation, name, hp,
        attack, defense, speed, sp_attack, sp_defense, height_m, weight_kg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pokemon_data["pokedex_number"],
        classification_id,
        pokemon_data["generation"], 
        pokemon_data["name"], 
        pokemon_data["hp"], 
        pokemon_data["attack"],
        pokemon_data["defense"],
        pokemon_data["speed"], 
        pokemon_data["sp_attack"], 
        pokemon_data["sp_defense"], 
        pokemon_data["height_m"],
        pokemon_data["weight_kg"],
    ))

    pokemon_cleanup = cursor.lastrowid

    #Now I just need to get the tricky types an abilities into the database

    #insert types
    for type_id in pokemon_data["types"]:
        cursor.execute("INSERT INTO pokemon_type (pokemon_id, type_id) VALUES (?, ?)", (pokemon_cleanup, type_id))

    #insert abilities 
    for ability_id in pokemon_data["abilities"]:
        cursor.execute("INSERT INTO pokemon_abilities (pokemon_id, ability_id) VALUES (?, ?)", (pokemon_cleanup, ability_id))


    print("pokemon has been added to database!")

    #commit those bad boi changes
    connection.commit()
    connection.close()
