# Importing Data

Importing data into the portal is a critical but delicate task. Unlike working with a spreadsheet or a single table, the portal relies on a complex **relational data model** that converts the relatively simple and flat GFHDB structure across multiple interconnected tables.

There are no off-the-shelf tools that fully support importing data into such a model. As a result, the process is custom-built, and while it is powerful, it is also sensitive to structure, formatting, and terminology. A small inconsistency — such as a misspelled method name or an unexpected unit — can prevent an entire file from being imported. However, with careful preparation, the process can be both predictable and efficient.

* * *

## Before You Import

Before beginning, you must download the official import template. Only files created using this template will be accepted. The template is provided in Microsoft Excel (`.xlsx`) format and reflects the current structure of the portal’s data model. You can find the link to the template here (replace with actual link).

Once you have downloaded the template, fill in your data carefully, making sure that each column is populated exactly as instructed in the column headers and accompanying notes. Vocabulary fields such as `method`, `rock type`, and `status` must use specific predefined terms. These are case-sensitive and must be entered exactly as expected. Units should also follow the conventions defined in the template.

:::{important}
It is strongly recommended that you do not change column headers or insert new sheets into the workbook. The importer expects a strict structure, and any deviation from the expected format **will likely result in errors**.
:::

<!-- This is a good place to include a **screenshot of the empty template**, with annotations pointing out controlled vocabulary fields, required columns, and any sheet tabs that must be completed. Consider highlighting common pitfalls, such as incorrect units or unsupported characters. -->

* * *

## How to Import Data

To begin the import process, navigate to the dataset you are working on and open the **Import Data** page. This can be found under the **Actions** section in the left-hand sidebar. Once there, you will see a simple form allowing you to upload your completed `.xlsx` file.

Click the upload button and select your file. Once the upload begins, the system will parse your data and attempt to validate it. If your file is correctly structured and all values are valid, the importer will proceed to load the data into the dataset.

:::{figure} /_static/import/import_form.png
:alt: Import Form Screenshot

Figure 1. Import Form
:::

* * *

## Help, I Have Errors!

If your import fails, don’t worry — this is a normal part of the process, especially early on.

The most common reason for failure is data that does not conform to the portal's strict type and vocabulary requirements. Unlike Excel, which will happily mix numbers, strings, and empty cells without complaint, the portal enforces strict types: a field defined as a number must be a number; a vocabulary field must match exactly one of the accepted terms.

When a validation error occurs, the system will return a clear error message identifying the sheet, row, and column where the problem was detected. These messages may include hints about expected values or types. In many cases, the problem will be a simple mismatch — for example, entering `Conductional` instead of `Conduction`, or using `Yes` instead of `True`.

Once you have corrected the error in your Excel file, you can re-upload it using the same process. There is no penalty for failed attempts, and you can upload revised files as many times as needed.

If the error message seems incorrect or unclear, or if you believe the problem may be a bug, please report it by opening an issue in the [GitHub repository](https://github.com/heatflow-portal/issues) or by contacting the portal administrators directly.

* * *

## Import Success

If the import is successful, you will be redirected automatically to the overview page for the dataset you are working on. A confirmation message will appear at the top of the screen to let you know that your data has been successfully imported.

From here, you can verify the imported content by navigating to the **Data** tab. Each section of the tab will reflect a part of the relational data model — for example, you may see lists of sites, boreholes, measurements, and linked references. Take some time to review the content and ensure that everything appears correctly.

It’s important to note that importing data does not immediately make it public. The dataset must still undergo review and be approved by a Data Administrator before it is published on the portal. Until then, your data remains private and editable only by the reviewers and administrators associated with the dataset.

This is a good place for a **screenshot of a successfully imported dataset**, showing the overview tab with a success message, and possibly the data tab with previewed rows.



## Common Issues

The following are some common issues that users encounter when importing data:

- Additional empty rows
- Incorrect date formats
- Misspelled controlled vocabulary terms
- Incorrect delimiters
- Missing required columns
- Use of commas instead of periods for decimal points
- Server timeouts for large files