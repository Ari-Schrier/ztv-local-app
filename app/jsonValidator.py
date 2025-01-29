import json

def validate_json(file_path):
    try:
        # Try to load the JSON file
        with open(file_path, 'r') as f:
            json.load(f)
        print("JSON is valid.")
        return True
    except json.JSONDecodeError as e:
        print(f"JSON is invalid: {e}")
        suggest_fixes(file_path, e)
        return False

def suggest_fixes(file_path, error):
    # Provide suggestions for common mistakes
    error_message = str(error)
    line_number = None
    
    # Try to extract line number from the error message
    if "line" in error_message:
        try:
            line_number = int(error_message.split("line")[1].split()[0])
        except ValueError:
            print(f"Value Error- {error_message}")

    print("\nPotential issues detected:")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()

     # Check for unbalanced brackets or braces
    open_brackets = 0
    starting_line = 0
    for i, line in enumerate(lines, start=1):
        open_brackets += line.count("{") - line.count("}")
        open_brackets += line.count("[") - line.count("]")
        starting_line += line.count("[")
        if starting_line > 1:
            print(f"Extra opening bracket detected at line {i}: {line.strip()}.\nThere should only be a single instance of '[' and ']' in the entire json, and they should be at the start end end of the file respectively")
            return
        if open_brackets < 0:
            print(f"Unbalanced closing bracket detected at line {i}: {line.strip()} Make sure all {'{'} and '[' have matching {'}'} and ']'.")
            open_brackets = 0
            return

    
    if open_brackets > 0:
        print("Unbalanced opening brackets detected. Make sure all '{' and '[' have matching '}' and ']'.")
        return
    
    if line_number:
        print(f"Error appears to be near line {line_number}:")
        print(f"{line_number}: {lines[line_number - 1].strip()}")

        # Suggest fixes
        if ":" not in lines[line_number - 1]:
            print("  - Missing colon? Check the key-value pair.")
        if "," not in lines[line_number - 1] and "}" not in lines[line_number - 1]:
            print("  - Missing a comma before or after this line?")
        if lines[line_number - 1].count(":") > 1:
            print("  - Too many colons? Use only one per key-value pair.")

if __name__ == "__main__":
    # Replace 'example.json' with the path to your JSON file
    validate_json("output/mexican_food/mexican_food.json")
