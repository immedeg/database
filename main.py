import csv
import os
import shutil
from dearpygui import dearpygui as dpg
import pandas as pd


phone_allowed_chars = set("+0123456789-")

class FileDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.fields = ["ID", "Name", "Passport", "Email", "Phone"]
        self.index = {}

    def create_db(self) -> str:
        if os.path.exists(self.db_file):
            return "Data base already exist"

        df = pd.DataFrame(columns=self.fields)
        df.to_csv(self.db_file, index=False)
        
        return "Data base created"

    def open_db(self) -> str:                                           # TODO
        if not os.path.exists(self.db_file):
            return "Data base not found"
        
        self._build_index()
        return "Data base is open"
    
    def clear_db(self) -> str:
        df = pd.read_csv(self.db_file)
        df.head(0).to_csv(self.db_file, index=False)
        self.index.clear()
        return "Data base is clear"

    def delete_db(self) -> str:
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
            self.index.clear()
            return "Data base was deleted"
        else:
            return "Data base not found"
            
    def add_record(self, record: dict[str, str]) -> str:
        key = record["ID"]
        if key in self.index:
            return f"ID {key} already exist"

        df = pd.DataFrame([record])
        df.to_csv(self.db_file, mode='a', index=False, header=False)
        
        self._build_index()
        return "Record added"

    def delete_record(self, field: str, value: str) -> str: 
        df = pd.read_csv(self.db_file)
        print(str(value))
        
        if field == "ID":
            df = df.drop(df[df.ID == int(value)].index)
            # print("FOUND ID")
        elif field == "Name":
            df = df.drop(df[df.Name == str(value)].index)
            # print("FOUND NAME")
        elif field == "Passport":
            df = df.drop(df[df.Passport == int(value)].index)
            # print("FOUND PASSPORT")
        elif field == "Email":
            df = df.drop(df[df.Email == str(value)].index)
            # print("FOUND EMAIL")
        elif field == "Phone":
            df = df.drop(df[df.Phone == int(value)].index)
            # print("FOUND PHONE")
            
        df.to_csv(self.db_file, index=False)

        self._build_index()
        return "Record(s) deleted"

    def search_records(self, field:str, value:str) -> str:
        output = f"{field}: {value}\nResults: "
        
        if field == "ID":
            if value not in self.index:
                output += "0\nNot found"
                return output
            message = self.search_records_ID(value=value).split(',')
            message = "  ".join(value for value in message)
            header_line = "  ".join(key for key in self.fields)
            output += '1\n' + header_line + '\n' + message
            
        else:
            df = pd.read_csv(self.db_file)
            
            if field == "Phone" or field == "Passport":
                res = df.loc[df[field] == int(value)]
            else:
                res = df.loc[df[field] == value]    
                
            output += str(res.shape[0]) + '\n'
            
            if res.shape[0] == 0:
                output += 'Not found'
            else:
                header_line = "  ".join(key for key in self.fields)
                output += header_line
                for row in range(res.shape[0]):
                    output = output + '\n' + ' '.join(list(str(res.values[row][i]) for i in range(5)))
        return output
        
        '''col_width = 30
        results = []
        output = field + ": " + value
        
        with open(self.db_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if field in row and row[field] == value:
                    results.append(row)

        if results:
            header_line = "".join(f"{key:<{col_width}}" for key in self.fields)
            output = output + '\n' + f"Results: {len(results)}\n" + header_line
            for record in results:
                line = "".join(f"{record[key]:<{col_width}}" for key in self.fields)
                output = output + '\n' + line
        else:
            output = output + "\nNot found"
        
        return output'''

    def search_records_ID(self, value:str) -> str: 
        if value not in self.index:
            print(value)
            return ""
        
        ind = self.index[value] - 1
        df = pd.read_csv(self.db_file)
        specific_row = df.iloc[ind]
        output = list(str(specific_row.values[i]) for i in range(5))
        output = ','.join(output)
        return output

    def edit_record(self, key: str, updated_record: dict[str, str]) -> str:
        if key not in self.index:
            return "Not found"
        
        cur_ind = self.index[key] - 1

        df = pd.read_csv(self.db_file) 
        
        for field in self.fields:
            if field == "ID":
                continue
            elif field == "Name" or field == "Email":
                df.loc[cur_ind, field] = updated_record[field]
            else:
                df.loc[cur_ind, field] = int(updated_record[field])
        
        df.to_csv(self.db_file, index=False) 
        self._build_index()
        return "Saved"

    def create_backup(self, backup_file: str) -> str:
        shutil.copy(self.db_file, backup_file)
        return "Backup created"

    def restore_backup(self, backup_file: str) -> str:
        shutil.copy(backup_file, self.db_file)
        self._build_index()
        return "Data base restored from backup"

    def import_xlsx(self, xlsx_file_name: str) -> str:
        try:
            df = pd.read_csv(self.db_file)
            xlsx_file = xlsx_file_name + ".xlsx"
            df.to_excel(xlsx_file, index=False, engine='openpyxl')
            return f"Import to file {xlsx_file}"
        except:
            return "Error importing file to xlsx"
            
    def _build_index(self) -> None:
        self.index.clear()
        with open(self.db_file, mode="r", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for position, row in enumerate(reader, start=1):
                self.index[row["ID"]] = position


class FileDatabaseGUI:
    def __init__(self):
        self.db = FileDatabase("database.csv")
        dpg.create_context()
        self.db._build_index()
        self.create_gui()
        

    def create_gui(self):
        dpg.create_viewport(title="Data Base Window", width=500, height=800)
        with dpg.font_registry():
            default_font = dpg.add_font("/System/Library/Fonts/HelveticaNeue.ttc", 15)
            second_font = dpg.add_font("/System/Library/Fonts/HelveticaNeue.ttc", 19)
            
        with dpg.window(label="Data base", width=500, height=800):
            dpg.add_text("General commands", tag="Text_1")
            
    # GENERAL
            with dpg.group(horizontal=True):
                dpg.add_button(label="Create DB", callback=lambda: self.create_data_base(), width=100, height=28)
                dpg.add_button(label="Save DB", callback=lambda: self.open_data_base(), width=100, height=28)
                dpg.add_button(label="Clear DB", callback=lambda: self.clear_data_base(), width=100, height=28)
                dpg.add_button(label="Delete DB", callback=lambda: self.delete_data_base(), width=100, height=28)    
            with dpg.group(horizontal=True):     
                dpg.add_button(label="Create backup", callback=lambda: self.create_backup(backup_file="backup.csv"), width=208, height=28) 
                dpg.add_button(label="Restore from backup", callback=lambda: self.restore(backup_file="backup.csv"), width=208, height=28) 
            dpg.add_separator()
            
    # IMPORT
            dpg.add_text("Import Data base to .xlsx file", tag="Text_5")
            with dpg.group(horizontal=True):
                dpg.add_input_text(label=".xlsx", tag="import_file_name", width=200)
                dpg.add_button(label="Import", callback=lambda: self.import_to_xlsx(), width=70, height=25)
            dpg.add_text("", tag="message_text_general")
            dpg.add_separator()
            
    # ADD 
            dpg.add_text("Add a record", tag="Text_2")
            for field in self.db.fields:
                dpg.add_input_text(label=field, tag=f"input_add_{field}", width=360)
            dpg.add_button(label="Add", callback=self.add_record, width=50, height=25)
            dpg.add_text("", tag="message_text_add") 
            dpg.add_separator()
            
    # SEARCH
            dpg.add_text("Search", tag="Text_3")
            dpg.add_input_text(tag="input_searching", width=360)
            FIELDS = {55: "ID", 56: "Name", 57: "Passport", 58: "Email", 59: "Phone"}
            with dpg.group(horizontal=True):
                dpg.add_text("By field: ")
                for field in self.db.fields:
                    dpg.add_button(label=field, callback=lambda field_name=str(field): self.searching(field_=FIELDS[field_name]))
            dpg.add_text("", tag="message_text_search") 
    
    # DELETE
            dpg.add_button(label="Delete records", tag="hidden_button", callback=lambda: self.delete_record(), show=False, width=200) 
            dpg.add_text("", tag="message_text_delete_rec")
            
            dpg.add_separator()
            
    # EDIT
            dpg.add_text("Edit record", tag="Text_4")
            dpg.add_input_text(label="ID", tag="input_edit_id", width=200)
            
            with dpg.group(tag="input_group", show=False, enabled=False):
                dpg.add_input_text(label="Name", tag="edit_name", default_value="", width=360)
                dpg.add_input_text(label="Passport", tag="edit_passport", default_value="", width=360)
                dpg.add_input_text(label="Email", tag="edit_email", default_value="", width=360)
                dpg.add_input_text(label="Phone", tag="edit_phone", default_value="", width=360)
            

            dpg.add_button(label="Find record", callback=self.edit_record, user_data="input_group", width=95) # , pos = (270, 587)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Edit", tag="enabled_state", callback=self.enabled_change, user_data="input_group", width=95, show=False)
                dpg.add_button(label="Save", tag="save_edit_data", callback=self.save_edit_data, user_data="input_group", width=95, show=False)
                
            dpg.add_text("", tag="edit_status_text")
            
            dpg.add_separator()

    # FONTS
            dpg.bind_font(default_font)
            dpg.bind_item_font("Text_1", second_font)
            dpg.bind_item_font("Text_2", second_font)
            dpg.bind_item_font("Text_3", second_font)
            dpg.bind_item_font("Text_4", second_font)
            dpg.bind_item_font("Text_5", second_font)

    def create_data_base(self) -> None:
        dpg.set_value("message_text_general", self.db.create_db())
    
    def open_data_base(self) -> None:
        dpg.set_value("message_text_general", self.db.open_db())
    
    def clear_data_base(self) -> None:
        dpg.set_value("message_text_general", self.db.clear_db())
        
    def delete_data_base(self) -> None:
        dpg.set_value("message_text_general", self.db.delete_db())
        
    def restore(self, backup_file: str) -> None:
        dpg.set_value("message_text_general", self.db.restore_backup(backup_file=backup_file))
    
    def create_backup(self, backup_file: str) -> None:
        dpg.set_value("message_text_general", self.db.create_backup(backup_file=backup_file))
    
    def add_record(self) -> None:
        record = {field: dpg.get_value(f"input_add_{field}") for field in self.db.fields}
        
        if "" in record.values():
            dpg.set_value("message_text_add", "Do not leave fields empty")
            return 0
        if not record["ID"].isdigit():
            dpg.set_value("message_text_add", "Invalid ID data")
            return 0
        if not record["Passport"].isdigit() or len(record["Passport"]) != 10:
            dpg.set_value("message_text_add", "Invalid passport data")
            return 0
        if set(record["Phone"]).issubset(phone_allowed_chars):
            record["Phone"] = record["Phone"].replace('+7', '8')
            if not record["Phone"].startswith('8') or len(record["Phone"]) != 11:
                dpg.set_value("message_text_add", "The phone number must consist of 11 digits (ex: 8-***-***-**-**)")
                return 0
            if not record["Phone"].isdigit():
                dpg.set_value("message_text_add", "The phone number must contain only following characters: +0123456789\nExample: +79005550011")
                return 0
            
        dpg.set_value("message_text_add", self.db.add_record(record=record))
        print(self.db.index)
    
    def searching(self, field_: str) -> None:
        self.selected_field = field_
        if len(dpg.get_value("input_searching")) == 0:
            return
        message = self.db.search_records(field=field_, value=dpg.get_value("input_searching"))
        dpg.set_value("message_text_search", message)
        if "Not found" not in message:
            dpg.configure_item("hidden_button", show=True)
        else:
            dpg.configure_item("hidden_button", show=False)
            
    def delete_record(self) -> None:
        message = self.db.delete_record(field=self.selected_field, value=dpg.get_value("input_searching"))
        dpg.set_value("message_text_delete_rec", message)
        dpg.configure_item("hidden_button", show=False)
        
    def edit_record(self, sender, app_data, user_data) -> None:
        id_num = dpg.get_value("input_edit_id")
        if id_num == "":
            return
        
        self.last_search_ind = id_num
        
        result = self.db.search_records_ID(str(id_num))
        
        group_id = user_data
        current_state_show = dpg.get_item_configuration(group_id)["show"]
        
        current_state_enable = dpg.get_item_configuration(group_id)["enabled"]
        if current_state_enable == True:
            dpg.configure_item(group_id, enabled=not current_state_enable)
            
        if result == "":
            dpg.set_value("edit_status_text", "No results")
            if current_state_show == True:
                dpg.configure_item(group_id, show=not current_state_show)
            dpg.configure_item("enabled_state", show=False)
            dpg.configure_item("save_edit_data", show=False)
            return
        
        else:
            dpg.set_value("edit_status_text", "")

        result = result.split(',')
        dpg.set_value("edit_name", result[1])
        dpg.set_value("edit_passport", result[2])
        dpg.set_value("edit_email", result[3])
        dpg.set_value("edit_phone", result[4])
        
        if current_state_show == False:
            dpg.configure_item(group_id, show=not current_state_show)
        dpg.configure_item("enabled_state", show=True) 
        dpg.configure_item("save_edit_data", show=False)
        
    def save_edit_data(self, sender, app_data, user_data) -> None:
        id_num = self.last_search_ind

        new_data = {"ID": id_num, "Name": "", "Passport": "", "Email": "", "Phone": ""}
        new_data["Name"] = dpg.get_value("edit_name")
        new_data["Passport"] = dpg.get_value("edit_passport")
        new_data["Email"] = dpg.get_value("edit_email")
        new_data["Phone"] = dpg.get_value("edit_phone")
        print(new_data)

        if not new_data["Passport"].isdigit() or len(new_data["Passport"]) != 10:
            dpg.set_value("edit_status_text", "Invalid passport data")
            return
        if set(new_data["Phone"]).issubset(phone_allowed_chars):
            new_data["Phone"] = new_data["Phone"].replace('+7', '8')
            if not new_data["Phone"].startswith('8') or len(new_data["Phone"]) != 11:
                dpg.set_value("edit_status_text", "The phone number must consist of 11 digits (ex: 8-***-***-**-**)")
                return
            if not new_data["Phone"].isdigit():
                dpg.set_value("edit_status_text", "The phone number must contain only following characters: +0123456789\nExample: +79005550011")
                return
        
        message = self.db.edit_record(id_num, new_data)
        dpg.set_value("edit_status_text",message)
        
        group_id = user_data
        current_state = dpg.get_item_configuration(group_id)["enabled"]
        dpg.configure_item(group_id, enabled=not current_state)
        dpg.configure_item("enabled_state", show=True)
        dpg.configure_item("save_edit_data", show=False)
        
    def enabled_change(self, sender, app_data, user_data) -> None:
        group_id = user_data
        current_state = dpg.get_item_configuration(group_id)["enabled"]
        dpg.configure_item(group_id, enabled=not current_state)
        dpg.configure_item("save_edit_data", show=True)
        dpg.configure_item("enabled_state", show=False)
        
    def import_to_xlsx(self) -> None:
        name = dpg.get_value("import_file_name")
        if len(name) == 0:
            return 
        message = self.db.import_xlsx(dpg.get_value("import_file_name"))
        dpg.set_value("message_text_general", message)
        
    
gui = FileDatabaseGUI()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
