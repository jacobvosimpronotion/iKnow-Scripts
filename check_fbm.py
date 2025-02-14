import csv
import json
import os
import re

sourceFile_fbm = os.path.join(os.path.dirname(__file__), "../inputfiles/import_fbm.json")
sourceFile_sem = os.path.join(os.path.dirname(__file__), "../inputfiles/import_sem.json")
destinationFile = os.path.join(os.path.dirname(__file__), "../outputfiles/validation_results.csv")

# Labels used in iKnow
lblIsGDNObjT = "Is GDN object type"
lblIsStructVT = "Is structured value type"
lblIsKernelVL = "Is kernel of value list"
lblValueListCode = "Value list code"
lblValueListLoc = "Value list location"

vError = "Error"
vWarning = "Warning"

# Errors
msgNameStartLowerCase = "Name of entity type starts with lowercase!"
msgNounFormMissing = "Noun form is missing!"
msgTermNotFound = "Name of entity type doesn't exist as preferred term in the semantic model!"

# Warnings
msgCapitalsInName = "Name of entity type has uppercase after 1st character."
msgNounFormChevrons = "Noun form has characters outside < and >."

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
            if custom_property.get('Name') == lblIsStructVT and 'true' in custom_property.get('Text',[]):
                return True
    return

# Function to check whether an EntityType is the kernel of a value list
def func_is_kernel_value_list(entity_type):
    if 'CustomProperties' in entity_type and 'CustomProperty' in entity_type['CustomProperties']:
        for custom_property in entity_type['CustomProperties']['CustomProperty']:
            if custom_property.get('Name') == lblIsKernelVL and 'true' in custom_property.get('Text',[]):
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

    vElementType = "EntityType"
    vEntityTypeName = entityType['Name']
    vEntityTypeNounForm = entityType.get('NounForm', None)
    vEntityTypeGUID = entityType['Id']
    vEntityTypeDeclFT = entityType['IsObjectifiedFromFactType']

    # Error: Name doesn't start with capital
    if not func_begint_met_hoofdletter(vEntityTypeName):
        rows.append([vElementType, vError, vEntityTypeName, msgNameStartLowerCase])
    
    # Warning: Capitals after first character, excluding 'BRO' at any position
    if not func_geen_hoofdletter_na_1e_teken(vEntityTypeName):
        rows.append([vElementType, vWarning, vEntityTypeName, msgCapitalsInName])

    # Error: Noun form is missing
    if not vEntityTypeNounForm:
        rows.append([vElementType, vError, vEntityTypeName, msgNounFormMissing])

    # Error: Noun form has other number of elements than variables of entity type
    if vEntityTypeNounForm:
        count = count_elements(vEntityTypeNounForm)
        # print(f"Number of elements: {count}")
        # TO BE FINISHED!

    # Warning: Noun form has characters outside chevrons
    if vEntityTypeNounForm:
        if not func_no_text_outside_chevrons(vEntityTypeNounForm):
            rows.append([vElementType, vWarning, vEntityTypeName, msgNounFormChevrons, vEntityTypeNounForm])

    # Error: Name of entity type doesn't exist in semantic model
    found_concept = next(
        (concept for language in semData['KnowledgeDomain']['ConceptModel']['Languages']['Language'] if language['Language'] == "en"
         for concept in language['Concept']
         for term in concept['Terms']['Term']
         if term['Preferred'] == True and term['Value'] == vEntityTypeName.lower()), None)
    if not found_concept:
        rows.append([vElementType, vError, vEntityTypeName, msgTermNotFound])
    
    # Error: CommunicationPattern for declaring entity type is not an allowed sentence
    fact_type = next((ft for ft in fbmData['knowledgeDomain']['FactBasedModel']['FactTypes']['FactType'] if ft['Id'] == vEntityTypeDeclFT), None)
    patterns = fact_type['CommunicationPatterns']['CommunicationPattern'] if fact_type else []
    for pattern in patterns:
        print(pattern['Text'].replace('â€Œ', '').replace('Â', ''))

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