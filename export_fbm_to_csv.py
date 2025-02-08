import json
import csv
import os

sourceFile_fbm = os.path.join(os.path.dirname(__file__), "../inputfiles/import_fbm.json")
destinationFile = os.path.join(os.path.dirname(__file__), "../outputfiles/export.csv")

# Labels used in iKnow
strIsGDNObjT = "Is GDN object type"
strKernelVL = "Is kernel of value list"
strIsStructVT = "Is structured value type"
strValueListLoc = "Value list location"

# Header row, so column titles
arrHeaderRow = ['EntityTypeName','NounForm','IsGDNObjectType','IsKernelValueList','ValueListLocation','NrOfFactTypes','FactTypeCode','FactTypeName','CommunicationPattern']

with open(sourceFile_fbm, 'r') as fbm:
        fbmData = json.load(fbm)

# Extract the relevant data
rows = []
for entity in fbmData['knowledgeDomain']['FactBasedModel']['EntityTypes']['EntityType']:

    # skip structured value types
    if entity.get('CustomProperties', {}).get('CustomProperty', []) and any(prop.get('Name') == strIsStructVT and 'true' in prop.get('Text',[]) for prop in entity.get('CustomProperties', {}).get('CustomProperty', [])):
        print("Skipping structured value type: " + entity.get('Name'))
        continue

    name = entity.get('Name')
    nounform = entity.get('NounForm')

    # GDN object type, if so
    gdn_object_type = 'No'
    for prop in entity.get('CustomProperties', {}).get('CustomProperty', []):
        if prop.get('Name') == strIsGDNObjT and 'true' in prop.get('Text',[]):
            gdn_object_type = 'Yes'

    # kernel value list, if so
    is_kernel_vl = 'No'
    for prop in entity.get('CustomProperties', {}).get('CustomProperty', []):
        if prop.get('Name') == strKernelVL and 'true' in prop.get('Text',[]):
            is_kernel_vl = 'Yes'

    # value list location
    value_list_location = None
    for prop in entity.get('CustomProperties', {}).get('CustomProperty', []):
        if prop.get('Name') == strValueListLoc and 'Text' in prop and prop['Text']:
            value_list_location = prop['Text'][0]

    # count fact types where role is played by this entity type
    nr_of_fact_types = 0
    for fact_type in fbmData['knowledgeDomain']['FactBasedModel']['FactTypes']['FactType']:
        for role in fact_type['Roles']['Role']:
            if role.get('IsPlayedByObjecttype') == entity.get('Id'):
                nr_of_fact_types = nr_of_fact_types + 1
                fact_type_code = fact_type.get('Code')
                fact_type_name = fact_type.get('Name')                
                fact_type_comm_pattern = fact_type.get('CommunicationPatterns', {}).get('CommunicationPattern', [None])[0].get('Text', None)
                # remove ZWNJ and NBSP characters from communication pattern
                if fact_type_comm_pattern:
                   fact_type_comm_pattern = fact_type_comm_pattern.replace('â€Œ', '').replace('Â', ' ')
                   print(fact_type_comm_pattern)
                # add row with fact type name
                rows.append([name, nounform, gdn_object_type, is_kernel_vl, value_list_location, nr_of_fact_types, fact_type_code, fact_type_name, fact_type_comm_pattern])
    # add row for entity type if no fact types are found
    if nr_of_fact_types == 0:
        rows.append([name, nounform, gdn_object_type, is_kernel_vl, value_list_location, nr_of_fact_types])

# Write the data to a CSV file
with open(destinationFile, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(arrHeaderRow)
    writer.writerows(rows)

print("Data successfully exported to " + destinationFile)