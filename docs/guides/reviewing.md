# Reviewing Literature

This guide explains how to review a literature item within the portal, extract relevant data and metadata, and prepare it 
for inclusion in the heat flow database. **Only authorized reviewers** have access to this functionality. If you would
like to become a reviewer, please contact the portal administrators.

* * *

## Selecting an Item to Review

:::{figure} /_static/review/review_list.png
:alt: Review List Screenshot

Figure 1. The Literature Review list page shows literature items that are available for review. To review an item, click 
the **"Start Review"** button at the bottom of the card (highlighted). If you don't see this button, the item may already 
be under review by someone else or might not be available for review. Check with portal administrators.
:::

- Navigate to the [Review List](https://portal.heatflow.world/reviews/) to view literature items that are available for review.
- Use the search bar on the left side of the page to filter items by title, author, publication year, or other available metadata.
- Each literature item is displayed as a "review card" containing basic bibliographic details.
- To claim an item, click the **"Start Review"** button located at the bottom of the card.

:::{note}
If you believe an item is missing or incorrectly marked as unavailable, please contact the portal administrators.
:::

* * *

## Starting the Review

:::{figure} /_static/review/starting_review.png
:alt: Start Review Screenshot

Figure 2. To begin your review, you must first enter some basic information using the form shown in this image. You can
edit these details later if needed.
:::

- After clicking **"Start Review"**, you will be redirected to a review initiation page.
- Fill out the following fields:

- **Reviewers**: This will default to your username. You can add additional reviewers (e.g., a collaborator) by typing their usernames.

    - If a reviewer does not yet exist in the system, click the ➕ icon on the right-hand side of the field to quickly create a new user profile.
- **Start Date**: If left blank, the current date and time will be used.

    - The start date field accepts **partial dates**. If the full date is not known, you may omit the day or month. At a minimum, the **year** is required (e.g., `1992`, `1992-06`, or `1992-06-15`).
- Click **"Start Review"** to officially begin the review.

- This action locks the item for other reviewers and creates a new **Dataset** linked to the selected literature item.

:::{note}
Reviewers listed here will automatically be added as **Contributors** to the newly created Dataset with the role of **"Data Curator"**. This is a DataCite-recognized role that ensures reviewers receive proper credit for their curation work in any future data publication or citation based on this dataset. If you need to modify this later, you can do so in the Dataset's **Contributors** tab.
:::

* * *

## Filling Out Metadata

Upon starting the review, you will be directed to the **Overview** tab of the new Dataset object. From here, you can 
navigate to the **Manage Dataset** tab using the sidebar on the left (under actions). This is where you will edit metadata 
for the Dataset.

For detailed guidance on filling out Dataset-level metadata, please refer to the [FairDM Documentation](https://fairdm.org/docs/metadata/).

:::{figure} /_static/review/dataset.png
:alt: Dataset Detail Screenshot

Figure 3. After starting the review, you will be redirected to the "Overview Page" of the new Dataset. Find the **Manage Dataset**
tab in the left sidebar to start editing metadata.
:::

In the **Basic Information** section below, it is strongly recommended that you:
- **Change the Dataset title** to something descriptive of the Dataset itself, rather than the literature item.
- Add a CC BY 4.0 license to the Dataset, which is required for publication.

You can also add other metadata here as you wish.

:::{figure} /_static/review/basic_information.png
:alt: Basic Information Screenshot

Figure 4. After starting the review, you will be redirected to the "Overview Page" of the new Dataset. Find the **Manage Dataset**
tab in the left sidebar to start editing metadata.
:::

Next, in the **Descriptions** section, it is strongly recommended that you add ***at a minimum*** an abstract summarizing 
the Dataset. This will help future users understand the Dataset's significance and content. It is also a good idea to describe
the methods involved in data collection (under **Methods**), and any other relevant context can be provided under **Other**.

:::{figure} /_static/review/descriptions.png
:alt: Descriptions

Figure 5. In the **Descriptions** section, you can add an abstract summarizing the Dataset, methods used in data collection, and any other relevant context.
:::

:::{tip}
Having trouble creating descriptive texts for the Dataset? Ask ChatGPT for help! You can use the following prompt followed
by the abstract of the article you are reviewing:

```markdown
I have a scientific article that I am reviewing in order to extract data and create a publishable dataset. The 
article comes with the following abstract. Please extract relevant information and produce an appropriate title for the dataset,
as well as an "abstract", "methods" and (if applicable) "other" description for the dataset. The title should be descriptive of the dataset itself, not the article.
```
:::

* * *

## Assigning Contributors

After adding appropriate metadata, you need to assign contributors to the Dataset. This is important for ensuring proper credit and attribution. Please refer to the [FairDM Documentation](https://fairdm.org/docs/metadata/) on how to add contributors and modify their roles.

**Who to add as a contributor?**

If the ***dataset has previously been published*** (e.g. with GFZ Data Services, Pangea, or other data repositories):
- Add the authors from the published dataset as contributors to this Dataset. Ignore authors listed on the literature item that are not listed as authors of the dataset.

***Otherwise:***
- Add the authors from the literature item as contributors to this Dataset.

:::{important}
Ensure that contributors from the published dataset or literature item are assigned the **Creator** role. This means they will be listed alongside this dataset within the portal and on any potential data publications that result from this dataset.
:::

:::{note}
Unless you are directly involved in the data collection or curation, you should edit you own role within the dataset. The system will automatically assign you as **Data Curator** based on your role as a reviewer.
:::

## Importing Data

Please refer to the [Importing Data Guide](guides/importing-data.md) in order to import data 
from a GHFDB structured spreadsheet into the current Dataset.

After importing data, you can verify that it everything worked as expected by navigating to the **Data** tab in the sidebar. Here, you will be able to view the imported data as it is represented in the portal database structure. If you are satisfied with the data, you can proceed to the next step.

* * *

## Submitting the Review

Once you have imported data, a new navigation item will appear in the sidebar called **"Submit Review"**. This is where you will finalize your review and submit it for approval.

:::{figure} /_static/review/submit_review.png
:alt: Submit Review Screenshot

Figure 6. In the **Descriptions** section, you can add an abstract summarizing the Dataset, methods used in data collection, and any other relevant context.
:::

On this page, you can update any further information about the review, such as:
- **Start Date**: If you did not set this when starting the review, you can set it here.
- **Completiong Date**: Leave this blank to use the current date, or set a specific completion date for the review. (Useful if the data were reviewed in the past and you are just filling out the review now.)
- **Reviewers**: Add or remove reviewers as needed. (Note: adding reviewers add this stage WILL NOT add them as contributors to the Dataset. If you want to add them as contributors, you must do so in the **Contributors** tab.)
- **Comments**: Add any comments or notes for the Data Administrator who will review your submission. This could be a summary of your findings, any issues encountered, or recommendations for acceptance or rejection. 

:::{figure} /_static/review/submit_review_form.png
:alt: Submit Review Form Screenshot

Figure 7. In the **Descriptions** section, you can add an abstract summarizing the Dataset, methods used in data collection, and any other relevant context.
:::

:::{note}
Comments are publicly visible so be sure to keep them professional and relevant to the review process.
:::

When you are satisfied with the review details, you can proceed to submit the review by clicking the **"Submit Review"** button at the bottom of the page.
This action locks the dataset for further editing by reviewers and sends a notification to data administrators for further review.

* * *

## What Happens Next?

A **Data Administrator** will be notified and will verify the dataset for:

- Metadata completeness and adherence to standards.
- Data integrity and proper formatting.
- Appropriate contributor attribution.

**Possible outcomes:**

- ✅ **Approved**: The dataset becomes publicly visible on the portal, and editing privileges are revoked.
- ❓ **Needs Revisions**: The Data Administrator may ask you to provide further information regarding the dataset or review process.
- ❌ **Rejected**: A dataset may be rejected if it does not meet the necessary standards of the portal and there is
no further means by which the dataset can be improved.

Once a decision has been made, you will be notified of the outcome by email or via the portal’s notification system.

:::{note}
If your review is rejected, it is not a reflection of your work as a reviewer. Rejections are usually based on the likelihood 
of recovering the necessary metadata in order to meet the standards of the portal. If it is determined that the dataset does not
meet these standards, and cannot be improved, it will be rejected.
:::

* * *

## Additional Notes

- You can abandon a review at any time by contacting an administrator, who can release the item for others to review.
- Keep detailed notes if the literature contains ambiguous or conflicting information.
- If a literature item covers multiple datasets (e.g., multiple regions or time periods), coordinate with other reviewers or administrators to split the review if needed.