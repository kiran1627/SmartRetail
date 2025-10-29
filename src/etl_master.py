# src/etl_master.py
import time
import os
import subprocess
import psutil
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

# Import ETL step modules
from data_cleaning import clean_sales_data
from monthly_sales import generate_monthly_sales
from rfm_segmentation import generate_rfm_scores
from sales_forecast import generate_sales_forecast
from export_powerbi import export_powerbi_data

console = Console()

# 🧩 Configure Power BI paths (update for your system)
PBIX_PATH = r"C:\Users\HP\SmartRetailBI\powerbi\SmartRetailBI.pbix"
PBI_EXE = r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"

def run_etl_pipeline():
    console.print(Panel.fit("🚀 [bold cyan]Smart Retail BI - ETL Pipeline Started[/bold cyan]", border_style="cyan"))
    start_time = time.time()

    with Progress() as progress:
        task = progress.add_task("[yellow]Running ETL steps...", total=6)

        try:
            # Step 1: Clean Data
            progress.update(task, description="[green]Step 1/6: Cleaning Data...[/green]")
            df_cleaned = clean_sales_data()
            progress.advance(task)

            # Step 2: Monthly Sales
            progress.update(task, description="[green]Step 2/6: Generating Monthly Sales...[/green]")
            df_monthly = generate_monthly_sales(df_cleaned)
            progress.advance(task)

            # Step 3: RFM Segmentation
            progress.update(task, description="[green]Step 3/6: Creating RFM Segments...[/green]")
            df_rfm = generate_rfm_scores(df_cleaned)
            progress.advance(task)

            # Step 4: Sales Forecast
            progress.update(task, description="[green]Step 4/6: Forecasting Future Sales...[/green]")
            df_forecast = generate_sales_forecast(df_monthly)
            progress.advance(task)

            # Step 5: Export Power BI Dataset
            progress.update(task, description="[green]Step 5/6: Exporting Power BI Dataset...[/green]")
            df_powerbi = export_powerbi_data()
            progress.advance(task)

            # Step 6: Auto-Launch & Refresh Power BI
            progress.update(task, description="[green]Step 6/6: Launching Power BI and refreshing data...[/green]")
            try:
                subprocess.Popen([PBI_EXE, PBIX_PATH])
                console.print("⏳ Waiting for Power BI to refresh data (3 mins)...")
                time.sleep(180)  # Wait for refresh
                # Close Power BI
                for proc in psutil.process_iter():
                    if "PBIDesktop.exe" in proc.name():
                        proc.terminate()
                console.print("✅ Power BI refreshed and closed successfully.")
            except Exception as e:
                console.print(f"[bold red]⚠️ Power BI Refresh Error:[/bold red] {e}")
            progress.advance(task)

        except Exception as e:
            console.print(f"[bold red]❌ ETL Step Failed:[/bold red] {e}")
            return

    total_time = round(time.time() - start_time, 2)
    console.print(Panel.fit(
        f"✅ [bold green]ETL + Power BI Refresh Completed in {total_time}s![/bold green]\n\n"
        "[white]Generated Files:[/white]\n"
        "📄 cleaned_sales.csv\n"
        "📄 monthly_sales.csv\n"
        "📄 rfm_scores.csv\n"
        "📄 sales_forecast.csv\n"
        "📄 powerbi_dataset.csv",
        border_style="green"
    ))

    # 🔹 Launch Streamlit Dashboard automatically
    console.print("\n🌐 [bold blue]Launching Streamlit Dashboard...[/bold blue]")
    try:
        os.system("streamlit run app/streamlit_app.py")
    except Exception as e:
        console.print(f"[bold red]⚠️ Could not start Streamlit:[/bold red] {e}")

if __name__ == "__main__":
    run_etl_pipeline()
