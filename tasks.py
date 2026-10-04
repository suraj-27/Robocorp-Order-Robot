from robocorp.tasks import task
from robocorp import browser

from RPA.PDF import PDF
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Archive import Archive

import os

BASE_URL = "https://robotsparebinindustries.com/#/robot-order"
ORDERS_URL = "https://robotsparebinindustries.com/orders.csv"

OUTPUT_DIR = "output"
RECEIPTS_DIR = os.path.join(OUTPUT_DIR, "receipts")
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")

@task
def order_robots_from_RobotSpareBin():
    """
    Order robots from RoboSpareBin Industries Inc.
    
    The Robot:
    - Download order.csv file.
    - complete all root orders.
    - save each order reciepts as a pdf.
    - save screenshot of each orderd robot.
    - Embed robot order screenshot with reciept pdf.
    - Create a zip archive containing all receipts.
    
    """
    browser.configure(
        slowmo=100
    )
    create_output_directories()
    
    open_robot_order__website()
    
    orders = get_orders()
    
    for order in orders:
        process_order(order)
        
    archive_receipts()
    
    
def create_output_directories():
    """Create directories required for output files"""
    
    os.makedirs(
        RECEIPTS_DIR,
        exist_ok=True
    )
    
    os.makedirs(
        SCREENSHOTS_DIR,
        exist_ok=True
    )
    
    
def open_robot_order__website():
    """open robospearbin order website
    and close initial popup
    """
    browser.goto(BASE_URL)
    page = browser.page()
    page.click("text=OK")


def get_orders():
    """
    Download orders.csv file and return
    it as table
    """
    http = HTTP()
    http.download(url=ORDERS_URL, overwrite=True)
    
    tables = Tables()
    orders = tables.read_table_from_csv('orders.csv', header=True)
    
    return orders

def process_order(order):
    """
    process one robot order
    """
    
    fill_order_form(order)
    
    preview_robot()
    
    submit_order(order)    
    
    
def fill_order_form(order):
    """
    fill data fetched from orders.csv
    """
    page = browser.page()
    
    #Robot Head
    page.select_option('#head', str(order['Head']))    
    
    #Robot Body
    page.click(f'input[name="body"][value="{order["Body"]}"]')
    
    #Robot legs
    page.fill('input[placeholder="Enter the part number for the legs"]', str(order['Legs']))
    
    #Address
    page.fill('#address', order['Address'])
    
    
def preview_robot():
    """
    Clicks the Preview button.
    """
    page = browser.page()
    page.click("#preview")
    
def submit_order(order):
    """
    submit the order.
    Retry until receipt appears
    """
    page = browser.page()
    while True:
        page.click('#order')
        
        # Check if receipt appears
        receipt = page.locator("#receipt")
        
        if receipt.is_visible():
            order_num  = str(order['Order number'])
            pdf_file = store_receipt_as_pdf(order_num)
            screenshot_file = screenshot_robot(order_num)
            embed_screenshot_to_receipt(screenshot_file, pdf_file)
            
            order_another_robot()
            
            return


def store_receipt_as_pdf(order_num):
    """
    Save order receipt as pdf
    """
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    
    pdf_path = os.path.join(RECEIPTS_DIR,f"{order_num}.pdf")
    
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, pdf_path)
    
    return pdf_path


def screenshot_robot(order_num):
    """
    Capture screenshot of the ordered robot
    """
    page = browser.page()
    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{order_num}.png")
    
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    
    return screenshot_path


def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """
    Add screenshot in receipt pdf file
    """
    pdf = PDF()
    
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot_path,
        source_path=pdf_path,
        output_path=pdf_path
    )
    
    
def order_another_robot():
    """
    Click on the order another robot button,
    and close pop up window
    """
    page = browser.page()
    page.click("#order-another")
    page.click("text=OK")
    
    
def archive_receipts():
    """
    Create zip file for all receipts
    """
    archive = Archive()
    archive.archive_folder_with_zip(
        RECEIPTS_DIR, 
        os.path.join(
            OUTPUT_DIR,
            "receipts.zip"
        )
    )
    
    
    
    
    
    
    
    
    






