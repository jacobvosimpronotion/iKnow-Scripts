import json
import re

sourceFile_fbm = "import_fbm.json"
sourceFile_sem = "import_sem.json"
destinationFile = "output.txt"

# Labels used in iKnow
strIsGDNObjT = "Is GDN object type"
strIsStructVT = "Is structured value type"
strIsKernelVL = "Is kernel of value list"
strValueListCode = "Value list code"
strValueListLoc = "Value list location"

strError = "ERROR: "
strWarning = "WARNING: "

# Errors
strErrNameStartLowerCase = "Naam begint met een kleine letter!"

# Warnings
strWarNameCapitals = "Naam heeft hoofdletters na 1e teken."

# Function to check whether a name starts with a capital
def func_begint_met_hoofdletter(naam):
    patroon = r'^[A-Z]'
    if re.match(patroon, naam):
        return True
    else:
        return False

# Function to check whether a name has no capitals except the first characters, excluding 'BRO' at any position
def func_geen_hoofdletter_na_1e_teken(naam):
    patroon = r'^(BRO|.)[a-z0-9\s-]*(BRO|[a-z0-9\s-]*)*$'
    if re.match(patroon, naam):
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

# open (or create) result file
outputFile = open(destinationFile, "w")

for entityType in fbmData['knowledgeDomain']['FactBasedModel']['EntityTypes']['EntityType']:
    # Skip entity types that are structured value types
    if func_is_structured_value_type(entityType):
         continue
    else:
        outputFile.write(entityType['Name'])

    if func_is_kernel_value_list(entityType):
        outputFile.write(" (= value list)")

    outputFile.write(':\n')

    # if func_is_structured_value_type(entityType):
    #     outputFile.write("Dit is een structured value type." + '\n')

    # Name should start with capital
    if not func_begint_met_hoofdletter(entityType['Name']):
        outputFile.write(strError + strErrNameStartLowerCase + '\n')
    
    # Maybe error when capitals after first character
    if not func_geen_hoofdletter_na_1e_teken(entityType['Name']):
        outputFile.write(strWarning + strWarNameCapitals + '\n')

    outputFile.write('\n')

    # # testje
    # if 'CustomProperties' in entityType:
    #     outputFile.write("Custom properties aanwezig")
    # else:
    #     outputFile.write("Geen custom properties aanwezig")
    # outputFile.write('\n'+'\n')
        





outputFile.close()

print("Klaar!")