import os
import pefile


def list_exported_functions(dll_path):
    #List the exported functions from the founded dll(s).
    print(f"\nExported functions from: {dll_path}")
    try:
        pe = pefile.PE(dll_path)

        if not hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            print(" [!] No exported functions found.")
            return

        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            name = exp.name.decode('utf-8') if exp.name else None
            addr = hex(pe.OPTIONAL_HEADER.ImageBase + exp.address)
            print(f"  Ordinal: {exp.ordinal}, Address: {addr}, Name: {name}")
    except Exception as e:
        print(f"  [!] Failed to parse {dll_path}: {e}")

#This fucntion scans the current directory and selects the dll's
def export_dll_functions_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.dll'):
            dll_path = os.path.join(directory, filename)
            list_exported_functions(dll_path)

#Run in the active directory,
if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    export_dll_functions_in_directory(current_directory)
