import os

def deleteStuff(parentDir):
    # File extensions to delete (lowercase)
    TARGET_EXTS = {".mp4", ".png"}

    # Dry run first — set to False to actually delete
    DRY_RUN = False

    for subfolder_name in os.listdir(PARENT_DIR):
        subfolder_path = os.path.join(PARENT_DIR, subfolder_name)

        # Only process immediate subfolders
        if not os.path.isdir(subfolder_path):
            continue

        # List files directly in this subfolder
        for entry in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, entry)

            # Skip directories (don’t recurse)
            if os.path.isdir(file_path):
                continue

            # Check the file extension
            _, ext = os.path.splitext(entry)
            if ext.lower() in TARGET_EXTS:
                if DRY_RUN:
                    print(f"[DRY RUN] Would delete: {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

    if DRY_RUN:
        print("\nDry run complete. If the list looks correct, set DRY_RUN = False to actually delete.")

if __name__ == "__main__":
    for i in range(9, 15):
        PARENT_DIR = f"C:\\MyCode\\ZTV\\ztv-local-app\\app\\wikipedia\\output\\november_{i}"
        deleteStuff(PARENT_DIR)