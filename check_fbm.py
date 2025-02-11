import csv
import json
import os
import re

sourceFile_fbm = os.path.join(os.path.dirname(__file__), "../inputfiles/import_fbm.json")
sourceFile_sem = os.path.join(os.path.dirname(__file__), "../inputfiles/import_sem.json")
destinationFile = os.path.join(os.path.dirname(__file__), "../outputfiles/validation_results.csv")

# Labels used in iKnow
strIsGDNObjT = "Is GDN object type"
strIsStructVT = "Is structured value type"
strIsKernelVL = "Is kernel of value list"
strValueListCode = "Value list code"
strValueListLoc = "Value list location"

strError = "Error"
strWarning = "Warning"

# Errors
strErrNameStartLowerCase = "Name of entity type starts with lowercase!"
strMsgNounFormMissing = "Noun form is missing!"
strMsgTermNotFound = "Name of entity type doesn't exist as preferred term in the semantic model!"

# Warnings
strWarNameCapitals = "Name of entity type has uppercase after 1st character."
strMsgNounFormChevrons = "Noun form has characters outside < and >."

# Header row, so column titles
arrHeaderRow = ['ElementKind','IssueType','ElementName','Message','Details']

def count_elements(text):
    # Use regular expression to find all elements between < and >
    elements = re.findall(r'<[^>]+>', text)
    return len(elements)

# Function to check whether a name starts with a capital
def func_begint_met_hoofdletter(naam):
    pattern = r'^[A-Z]'
    if re.match(pattern, naam):
        return True
    else:
        return False

# Function to check whether a name has no capitals except the first characters, excluding 'BRO' at any position
def func_geen_hoofdletter_na_1e_teken(naam):
    pattern = r'^(BRO|.)[a-z0-9\s-]*(BRO|[a-z0-9\s-]*)*$'
    if re.match(pattern, naam):
        return True
    else:
        return False

# Function to check whether the noun form has text outside chevrons
def func_no_text_outside_chevrons(noun_form):
    pattern = r'^<[^>]+>(<[^>]+>)*$'
    if re.match(pattern, noun_form):
        return True
    else:
        return False

# Function to check whether an EntityType is a structured value type
def func_is_structured_value_type(entity_type):
    if 'CustomProperties' in entity_type and 'CustomProperty' in entity_type['CustomProperties']:
        for custom_property in entity_type['CustomProperties']['CustomProperty']:
            if custom_property.get('Name') == strIsStructVT and 'true' in custom_property.get('Text',[]):
                return True
    return

# Function to check whether an EntityType is the kernel of a value list
def func_is_kernel_value_list(entity_type):
    if 'CustomProperties' in entity_type and 'CustomProperty' in entity_type['CustomProperties']:
        for custom_property in entity_type['CustomProperties']['CustomProperty']:
            if custom_property.get('Name') == strIsKernelVL and 'true' in custom_property.get('Text',[]):
                return True
    return

with open(sourceFile_fbm, 'r') as fbm:
        fbmData = json.load(fbm)

with open(sourceFile_sem, 'r') as sem:
        semData = json.load(sem)

rows = []

# open (or create) result file
try:
    outputFile = open(destinationFile, "w")
except IOError:
    print(f"Error: The file {destinationFile} is already open or cannot be written to.")
    exit(1)

for entityType in fbmData['knowledgeDomain']['FactBasedModel']['EntityTypes']['EntityType']:
        
    # Skip entity types that are structured value types
    if func_is_structured_value_type(entityType):
         continue

    strElementType = "EntityType"
    strEntityTypeName = entityType['Name']
    strEntityTypeNounForm = entityType.get('NounForm', None)

    # Error: Name doesn't start with capital
    if not func_begint_met_hoofdletter(strEntityTypeName):
        rows.append([strElementType, strError, strEntityTypeName, strErrNameStartLowerCase])
    
    # Warning: Capitals after first character, excluding 'BRO' at any position
    if not func_geen_hoofdletter_na_1e_teken(strEntityTypeName):
        rows.append([strElementType, strWarning, strEntityTypeName, strWarNameCapitals])

    # Error: Noun form is missing
    if not strEntityTypeNounForm:
        rows.append([strElementType, strError, strEntityTypeName, strMsgNounFormMissing])

    # Error: Noun form has other number of elements than variables of entity type
    if strEntityTypeNounForm:
        count = count_elements(strEntityTypeNounForm)
        print(f"Number of elements: {count}")

    # Warning: Noun form has characters outside chevrons
    if strEntityTypeNounForm:
        if not func_no_text_outside_chevrons(strEntityTypeNounForm):
            rows.append([strElementType, strWarning, strEntityTypeName, strMsgNounFormChevrons, strEntityTypeNounForm])

    # Error: Name of entity type doesn't exist in semantic model
    found_concept = next(
        (concept for language in semData['KnowledgeDomain']['ConceptModel']['Languages']['Language'] if language['Language'] == "en"
         for concept in language['Concept']
         for term in concept['Terms']['Term']
         if term['Preferred'] and term['Value'] == strEntityTypeName.lower()), None)
    if not found_concept:
        rows.append([strElementType, strError, strEntityTypeName, strMsgTermNotFound])
    
    # if not any(entityType['Name'] == entity['Name'] for entity in semData['knowledgeDomain']['ConceptModel']['Languages']['Language']['Concept']['Entity']):
    #     rows.append([strElementType, strError, strEntityTypeName, "Name doesn't exist in semantic model"])

    # # testje
    # if 'CustomProperties' in entityType:
    #     outputFile.write("Custom properties aanwezig")
    # else:
    #     outputFile.write("Geen custom properties aanwezig")
    # outputFile.write('\n'+'\n')
        
# for factType in fbmData['knowledgeDomain']['FactBasedModel']['FactTypes']['FactType']:
#     outputFile.write(factType['Name'] + '\n')

# Write the data to a CSV file
with open(destinationFile, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(arrHeaderRow)
    rows.sort(key=lambda x: (x[0], x[2]))
    writer.writerows(rows)

print("Validation finished and results written to " + destinationFile)