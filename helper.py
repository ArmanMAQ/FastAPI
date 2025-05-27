import os
import csv
import time
import datetime
from queue import Queue
from threading import Thread
import openpyxl
import clr_loader
from pythonnet import load
# Use coreclr instead of default (which becomes mono on Linux)
load("coreclr")
import uuid # For unique filenames
# import clr
from fastapi.responses import JSONResponse
# clr.AddReference("Microsoft.AnalysisServices.AdomdClient")
from pyadomd import Pyadomd



# Global dictionary to store job statuses
job_statuses = {}

query = f"""
        EVALUATE
        TOPN(
            10000,
            SELECTCOLUMNS(
                SAMPLELARGEDATASET,
                "id", SAMPLELARGEDATASET[id],
                "homepage", SAMPLELARGEDATASET[homepage],
                "genres_list", SAMPLELARGEDATASET[genres_list],
                "title", SAMPLELARGEDATASET[title],
                "imdb_id", SAMPLELARGEDATASET[imdb_id],
                "Cast_list", SAMPLELARGEDATASET[Cast_list],
                "Certificate", SAMPLELARGEDATASET[Certificate],
                "adult", SAMPLELARGEDATASET[adult],
                "keywords", SAMPLELARGEDATASET[keywords],
                "original_title", SAMPLELARGEDATASET[original_title],
                "Director", SAMPLELARGEDATASET[Director],
                "original_language", SAMPLELARGEDATASET[original_language],
                "overview", SAMPLELARGEDATASET[overview],
                "Poster_Link", SAMPLELARGEDATASET[Poster_Link],
                "poster_path", SAMPLELARGEDATASET[poster_path],
                "Producers", SAMPLELARGEDATASET[Producers],
                "production_companies", SAMPLELARGEDATASET[production_companies],
                "production_countries", SAMPLELARGEDATASET[production_countries],
                "spoken_languages", SAMPLELARGEDATASET[spoken_languages],
                "tagline", SAMPLELARGEDATASET[tagline]
            ),
            [id]
        )
        """


# --- Flask API Endpoint ---

def export_data_route(data):
    # Extract connection string and query from the request
    conn_str = data.get('conn_str') #!Change as per your requirement
    print(f"Connection string: {conn_str}")
    if not conn_str:
        return JSONResponse(content={"error": "Connection string is required"}, status_code=400)
    dax_query = query #!Change as per your requirement / data.get('dax_query')

    file_type = data.get('file_type')
    print(f"File type requested: {file_type}")

    filename_base = data.get('filename_base', f"exported_data_{uuid.uuid4()}")  # Generate a unique filename if not provided
    print(f"Filename base: {filename_base}")
    if file_type == 'excel':
        filepath = os.path.join(f"exportOutput/{filename_base}.xlsx")
        return write_batches_to_excel(conn_str, dax_query, filepath, batch_size=1000)
    elif file_type == 'csv':
        filepath = os.path.join(f"exportOutput/{filename_base}.csv")
        return write_batches_to_csv(conn_str, dax_query, filepath, batch_size=1000)
    else:
        return JSONResponse(content={"error": "Invalid file type specified. Choose 'excel' or 'csv'."}, status_code=400)

def run_batch_query(conn_str: str, dax_query: str, batch_size=10000):
    """
    Executes the provided DAX query and yields the results in batches.
    This is useful for large datasets to avoid memory issues.
    The batch size can be adjusted based on the available memory.
    """
    with Pyadomd(conn_str) as conn:
        with conn.cursor().execute(dax_query) as cur:
            columns = [col[0] for col in cur.description]
            first_batch = True
            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break
                yield columns, rows

def write_batches_to_excel(conn_str: str, dax_query: str,filepath:str, batch_size=10000):
    """
    Consumes batches yielded by run_export_batch and writes them to an Excel file.
    """
    runtimes= []
   
    start_time = time.time()
    wb = openpyxl.Workbook(write_only=True)  # Use write_only mode for performance
    ws = wb.create_sheet()
    row_count = 0
    i = 1
    for columns, rows in run_batch_query(conn_str, dax_query, batch_size):
        if row_count == 0:
            ws.append(columns)
        for row in rows:
            ws.append(row)
            row_count += 1
        print(f'Batch {i} written with {len(rows)} rows')
        i += 1
    wb.save(filepath)
    print(f'Data exported to {filepath}')
    end_time = time.time()
    run_time = end_time - start_time
    runtimes.append([10000, run_time])
    print(f"Execution time (10000): {end_time - start_time:.2f} seconds")
    #send run time as response
    return {"message": "Data export completed", "filepath": filepath, "execution_time": run_time}

def write_batches_to_csv(conn_str: str, dax_query: str, filepath: str, batch_size=10000):
    """
    Consumes batches yielded by run_export_batch and writes them to a CSV file.
    """
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:  # <-- Add encoding
        writer = csv.writer(csvfile)
        i = 1
        wrote_header = False
        for columns, rows in run_batch_query(conn_str, dax_query, batch_size):
            if not wrote_header:
                writer.writerow(columns)
                wrote_header = True
            writer.writerows(rows)
            if i % 10 == 0:
                print(f'Batch {i} written with {len(rows)} rows')
            i += 1
    print(f'Data exported to {filepath}')
    return {"message": "Data export completed", "filepath": filepath}