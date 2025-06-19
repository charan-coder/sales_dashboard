# SKU to MSKU Mapper

This application provides a graphical user interface (GUI) to map Stock Keeping Units (SKUs) to Master SKUs (MSKUs). It supports individual and combo products, handles various file formats, and logs all operations.

## Features

- Upload SKU data from CSV or Excel files.
- Load a separate mapping file (CSV or Excel) containing SKU-to-MSKU relationships.
- Automatically maps SKUs to MSKUs.
- Handles combo products (multiple SKUs mapping to a single MSKU).
- Logs successful mappings and errors for missing mappings.
- Outputs a cleaned and mapped dataset as a downloadable file.

## Setup

1.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

2.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1.  **Run the application:**
    ```bash
    python sku_mapper.py
    ```

2.  **Prepare your files:**

    *   **SKU Data File (CSV/Excel):** This file should contain a column named `SKU` that lists the SKUs you want to map.

        Example (`skus.csv`):
        ```csv
        OrderID,SKU,Quantity
        1001,SKU-A,1
        1002,SKU-B,2
        1003,SKU-C,1
        1004,SKU-D,5
        ```

    *   **Mapping File (CSV/Excel):** This file defines the relationship between SKUs and MSKUs. It must have two columns: `SKU` and `MSKU`.

        - For **individual products**, each row maps one SKU to one MSKU.
        - For **combo products**, list all SKUs in the combo separated by a comma (or another delimiter) in the `SKU` column, and specify the single resulting MSKU.

        Example (`mapping.csv`):
        ```csv
        SKU,MSKU
        SKU-A,MSKU-001
        SKU-B,MSKU-002
        SKU-C,MSKU-002
        SKU-A,SKU-B,MSKU-COMBO-AB
        ```

3.  **Using the GUI:**
    - Click **"Load SKU File"** to select your SKU data file.
    - Click **"Load Mapping File"** to select your mapping file.
    - Click **"Map SKUs"** to start the mapping process.
    - The log window will show the progress and any errors.
    - Once mapping is complete, a dialog will ask you where to save the output file.

## Output

The output file will be a CSV containing the original data with an added `MSKU` column. For SKUs that could not be mapped, the `MSKU` field will be empty.

Example (`output.csv`):
```csv
OrderID,SKU,Quantity,MSKU
1001,SKU-A,1,MSKU-001
1002,SKU-B,2,MSKU-002
1003,SKU-C,1,MSKU-002
1004,SKU-D,5,MAPPING_NOT_FOUND
```
