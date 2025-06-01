import os

def create_documentation_structure(root_path):
    # Folder structure as a dictionary
    folder_structure = {
        "Technical_Documents": ["Assembly_Guides", "User_Manuals", "Design_Specifications"],
        "Production_Files": ["CAD_Files", "Firmware", "Software_Tools"],
        "Bill_of_Materials (BOM)": [],
        "Certifications": ["CE_Compliance", "Other_Certifications"],
        "Risk_Assessment": [],
        "Quality_Control": ["Inspection_Reports", "Testing_Procedures"],
        "Change_Logs": [],
        "Legal_and_Regulatory": ["Warranty_Information", "Compliance_Statements"],
        "Contributions": [],
        "Issue_Tracking": []
    }

    # Create root directory
    if not os.path.exists(root_path):
        os.mkdir(root_path)

    # Create subdirectories
    for main_folder, sub_folders in folder_structure.items():
        main_folder_path = os.path.join(root_path, main_folder)
        if not os.path.exists(main_folder_path):
            os.mkdir(main_folder_path)
        if not os.path.exists(os.path.join(main_folder_path, ".gitkeep")):
            # also create a .gitkeep file in each subfolder
            with open(os.path.join(main_folder_path, ".gitkeep"), "w") as f:
                pass

        for sub_folder in sub_folders:
            sub_folder_path = os.path.join(main_folder_path, sub_folder)
            if not os.path.exists(sub_folder_path):
                os.mkdir(sub_folder_path)
            if not os.path.exists(os.path.join(sub_folder_path, ".gitkeep")):
                # also create a .gitkeep file in each subfolder
                with open(os.path.join(main_folder_path, ".gitkeep"), "w") as f:
                    pass

    print(f"Documentation structure created at {root_path}")

# Example usage
create_documentation_structure("./3D_Printer_Kit_Documentation")

