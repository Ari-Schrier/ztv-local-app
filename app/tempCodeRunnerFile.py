    from AI.stableFunctions import getPathToImage
    with open(f"output/{title}/{title}.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
    # for i in range(0, len(json_data)):
    for i in [5]:
        json_data[i]["id"] = i
        print(f"Processing image {i}/{len(json_data)-1} (This will take a bit)")
        path = getPathToImage(title, json_data[i]["prompt"], i, ratio = "1:1")
        path = f"output/{title}/images/{i}.png"
        json_data[i]["image_path"] = path
        print("Processed!")
    with open(f"output/{title}/{title}.json", "w") as file:
        json.dump(json_data, file, indent=4)