import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='sku_mapper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SkuMapperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SKU to MSKU Mapper")
        self.root.geometry("800x600")

        self.sku_file_path = ""
        self.mapping_file_path = ""
        self.sku_df = None
        self.mapping_df = None

        # --- GUI Elements ---
        # Frame for file selection
        file_frame = tk.Frame(root, pady=10)
        file_frame.pack(fill=tk.X)

        self.btn_load_sku = tk.Button(file_frame, text="Load SKU File", command=self.load_sku_file)
        self.btn_load_sku.pack(side=tk.LEFT, padx=10)

        self.lbl_sku_file = tk.Label(file_frame, text="No SKU file loaded", fg="red")
        self.lbl_sku_file.pack(side=tk.LEFT)

        self.btn_load_mapping = tk.Button(file_frame, text="Load Mapping File", command=self.load_mapping_file)
        self.btn_load_mapping.pack(side=tk.LEFT, padx=10)

        self.lbl_mapping_file = tk.Label(file_frame, text="No mapping file loaded", fg="red")
        self.lbl_mapping_file.pack(side=tk.LEFT)

        # Frame for mapping execution
        map_frame = tk.Frame(root, pady=10)
        map_frame.pack(fill=tk.X)

        self.btn_map = tk.Button(map_frame, text="Map SKUs", command=self.map_skus, state=tk.DISABLED)
        self.btn_map.pack(pady=10)

        # Log window
        log_frame = tk.LabelFrame(root, text="Log", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        logging.info(message)

    def load_file(self, file_type):
        path = filedialog.askopenfilename(filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ])
        if not path:
            return None, None

        try:
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            self.log(f"Successfully loaded {file_type} file: {path}")
            return path, df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {path}.\nError: {e}")
            self.log(f"Error loading {path}: {e}")
            return None, None

    def load_sku_file(self):
        path, df = self.load_file("SKU")
        if path:
            if 'SKU' not in df.columns:
                messagebox.showerror("Error", "SKU file must contain a 'SKU' column.")
                self.log("Error: SKU file is missing the 'SKU' column.")
                return
            self.sku_file_path = path
            self.sku_df = df
            self.lbl_sku_file.config(text=path.split('/')[-1], fg="green")
            self.check_files_loaded()

    def load_mapping_file(self):
        path, df = self.load_file("mapping")
        if path:
            if 'SKU' not in df.columns or 'MSKU' not in df.columns:
                messagebox.showerror("Error", "Mapping file must contain 'SKU' and 'MSKU' columns.")
                self.log("Error: Mapping file is missing 'SKU' or 'MSKU' columns.")
                return
            self.mapping_file_path = path
            self.mapping_df = df
            self.lbl_mapping_file.config(text=path.split('/')[-1], fg="green")
            self.check_files_loaded()

    def check_files_loaded(self):
        if self.sku_file_path and self.mapping_file_path:
            self.btn_map.config(state=tk.NORMAL)

    def map_skus(self):
        if self.sku_df is None or self.mapping_df is None:
            messagebox.showerror("Error", "Please load both SKU and mapping files first.")
            return

        self.log("Starting SKU mapping process...")

        # Create a mapping dictionary
        # Handle potential multiple SKUs in mapping file for combos
        mapping_dict = {}
        for _, row in self.mapping_df.iterrows():
            sku = str(row['SKU'])
            msku = str(row['MSKU'])
            # Handle combo SKUs, assuming they are comma-separated
            if ',' in sku:
                # Sort to handle different orderings
                combo_skus = tuple(sorted([s.strip() for s in sku.split(',')]))
                mapping_dict[combo_skus] = msku
            else:
                mapping_dict[sku.strip()] = msku

        # Function to find MSKU for a given SKU
        def get_msku(sku):
            sku = str(sku).strip()
            # Direct match
            if sku in mapping_dict:
                return mapping_dict[sku]
            
            # Check for combo product matches (simple case)
            # This part can be expanded for more complex combo logic
            # For now, we rely on the mapping file defining combos explicitly

            self.log(f"Warning: No mapping found for SKU: {sku}")
            return "MAPPING_NOT_FOUND"

        # Apply the mapping
        self.sku_df['MSKU'] = self.sku_df['SKU'].apply(get_msku)
        self.log("Mapping process completed.")

        self.save_output_file()

    def save_output_file(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")],
            title="Save Mapped File"
        )
        if not save_path:
            self.log("Save cancelled by user.")
            return

        try:
            if save_path.endswith('.csv'):
                self.sku_df.to_csv(save_path, index=False)
            else:
                self.sku_df.to_excel(save_path, index=False)
            self.log(f"Mapped file saved to: {save_path}")
            messagebox.showinfo("Success", f"Mapped file saved successfully to\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file.\nError: {e}")
            self.log(f"Error saving file to {save_path}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkuMapperApp(root)
    root.mainloop()
