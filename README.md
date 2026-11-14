### **Script Summary**

This script automates the generation of physical **Merit Badge Pocket Certificates** by merging Scout advancement records from an Excel spreadsheet onto a standardized PDF template.

#### **Key Features & Process Flow:**
1. **Environment & Directory Setup:** Installs `pymupdf` (for PDF manipulation) and navigates to the shared Google Drive folder containing the template and assets.
2. **Template Coordinate Extraction:** Opens the template PDF (`merit_badge_pocket_cert_template.pdf`) and dynamically extracts the layout coordinates (bounding boxes) for form fields (e.g., *Name*, *Badge*, *Date*, *Unit*, *Council*, and *Unit Leader* signature) based on their slot numbers (1 through 8 per page).
3. **Data Loading:** Loads the Scout records from the specified csv-file (`Merit_Badges_by_Scout.csv`) in their exact original order.
4. **Batch PDF Generation:**
   - Groups the records into batches of 8 per page to fit the physical card printing template.
   - Generates a multi-page PDF document.
   - Automatically scales text font sizes dynamically so longer Scout names or Merit Badge titles fit perfectly inside their bounding boxes without clipping.
   - Stamps a digital signature image (`signature.png`) on the designated signature line for each slot.
5. **Calibration Adjustments:** Includes precise `X_OFFSET` and `Y_OFFSET` configuration parameters to easily adjust alignment and compensate for printer margins.