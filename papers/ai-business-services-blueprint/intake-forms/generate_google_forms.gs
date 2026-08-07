/**
 * Generates live Google Forms for the Phase 0 (zero-meeting) intake forms
 * defined in ../CHECKLIST.md and the per-category files in this folder.
 *
 * HOW TO RUN
 * 1. Go to https://script.google.com -> New project.
 * 2. Delete the placeholder code, paste this whole file in.
 * 3. Click Run > createIntakeForms. Authorize when prompted (this script
 *    only touches Forms/Sheets/Drive files it creates itself).
 * 4. When it finishes, open the "Intake Forms — Links" spreadsheet it
 *    creates in your Drive root — it lists the editor URL and the live
 *    "share with clients" URL for each of the 10 forms.
 *
 * Re-running creates a fresh set of forms each time (it does not update
 * existing ones) — delete the old ones first if you're regenerating.
 */

function createIntakeForms() {
  var forms = getFormDefinitions();
  var results = [];

  forms.forEach(function (spec) {
    var form = FormApp.create(spec.title);
    form.setDescription(spec.description);
    form.setCollectEmail(true);

    addCommonFields(form);

    spec.fields.forEach(function (f) {
      addField(form, f);
    });

    results.push([spec.title, form.getEditUrl(), form.getPublishedUrl()]);
  });

  writeResultsSheet(results);
}

function addCommonFields(form) {
  form.addTextItem().setTitle('Business name').setRequired(true);
  form.addTextItem().setTitle('Contact name').setRequired(true);
  form
    .addTextItem()
    .setTitle('Contact phone (optional — text/SMS only, not a call request)')
    .setRequired(false);
}

function addField(form, f) {
  var item;
  switch (f.type) {
    case 'text':
      item = form.addTextItem().setTitle(f.label).setRequired(!!f.required);
      break;
    case 'paragraph':
      item = form
        .addParagraphTextItem()
        .setTitle(f.label)
        .setRequired(!!f.required);
      break;
    case 'checkbox':
      item = form
        .addCheckboxItem()
        .setTitle(f.label)
        .setChoiceValues(f.options)
        .setRequired(!!f.required);
      break;
    case 'multipleChoice':
      item = form
        .addMultipleChoiceItem()
        .setTitle(f.label)
        .setChoiceValues(f.options)
        .setRequired(!!f.required);
      break;
    case 'file':
      item = form
        .addFileUploadItem()
        .setTitle(f.label)
        .setRequired(!!f.required);
      break;
    default:
      throw new Error('Unknown field type: ' + f.type);
  }
  return item;
}

function writeResultsSheet(results) {
  var ss = SpreadsheetApp.create('Intake Forms — Links');
  var sheet = ss.getActiveSheet();
  sheet.appendRow(['Service', 'Edit URL (yours)', 'Live URL (send to clients)']);
  results.forEach(function (row) {
    sheet.appendRow(row);
  });
  sheet.autoResizeColumns(1, 3);
  Logger.log('Summary sheet: ' + ss.getUrl());
}

function getFormDefinitions() {
  var STANDARD_TURNAROUND = {
    type: 'multipleChoice',
    label: 'Turnaround needed',
    options: ['Standard', 'Rush'],
    required: true,
  };
  var BUDGET = {
    type: 'text',
    label: 'Budget range',
    required: true,
  };

  return [
    {
      title: 'OCR Data Extraction — Intake',
      description:
        'Send us scanned documents or images and tell us what data to pull out. No call needed — this form is all we need to scope and price the job.',
      fields: [
        {
          type: 'file',
          label: 'Upload: scanned documents / images',
          required: true,
        },
        {
          type: 'paragraph',
          label: 'Data fields to extract (list them)',
          required: true,
        },
        {
          type: 'multipleChoice',
          label: 'Output format',
          options: ['CSV', 'Excel', 'JSON'],
          required: true,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'AI Data Entry — Intake',
      description:
        'Send us your source data and tell us where it needs to go. No call needed.',
      fields: [
        { type: 'file', label: 'Upload: source data', required: true },
        {
          type: 'text',
          label: 'Destination system (spreadsheet / CRM / database — name it)',
          required: true,
        },
        {
          type: 'paragraph',
          label:
            'Field mapping — which source fields go to which destination fields',
          required: true,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'Invoice Processing — Intake',
      description:
        'Send us your invoices and tell us what data you need extracted. No call needed.',
      fields: [
        {
          type: 'file',
          label: 'Upload: invoices (or paste a shared-folder link below)',
          required: false,
        },
        {
          type: 'text',
          label: 'Shared-folder link (if not uploading directly)',
          required: false,
        },
        {
          type: 'checkbox',
          label: 'Data fields needed',
          options: ['Vendor', 'Amount', 'Date', 'PO number', 'Line items'],
          required: true,
        },
        {
          type: 'multipleChoice',
          label: 'Output format',
          options: ['CSV', 'Excel', 'JSON'],
          required: true,
        },
        {
          type: 'text',
          label: 'Accounting system to import into (if any)',
          required: false,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'Receipt Processing — Intake',
      description:
        'Send us your receipts and how you want them categorized. No call needed.',
      fields: [
        { type: 'file', label: 'Upload: receipts', required: true },
        {
          type: 'paragraph',
          label:
            'Expense categories to sort into (list them, or write "use standard")',
          required: true,
        },
        { type: 'text', label: 'Output format', required: true },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'Document Digitization — Intake',
      description:
        'Send us scans (or shipping/drop-off instructions for physical documents) and how you want the digital files organized. No call needed.',
      fields: [
        {
          type: 'file',
          label: 'Upload: scans (skip if shipping physical documents)',
          required: false,
        },
        {
          type: 'paragraph',
          label: 'Shipping / drop-off instructions (if applicable)',
          required: false,
        },
        {
          type: 'multipleChoice',
          label: 'Output format needed',
          options: ['PDF', 'Word', 'Searchable PDF'],
          required: true,
        },
        {
          type: 'paragraph',
          label: 'Naming and organization scheme preference',
          required: false,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'Spreadsheet Cleanup — Intake',
      description:
        'Send us the spreadsheet and what needs fixing. No call needed.',
      fields: [
        { type: 'file', label: 'Upload: spreadsheet to clean', required: true },
        {
          type: 'checkbox',
          label: 'Issues to fix',
          options: [
            'Duplicates',
            'Formatting',
            'Missing data',
            'Broken formulas',
          ],
          required: true,
        },
        {
          type: 'paragraph',
          label: 'Desired final structure (or write "match existing")',
          required: false,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'PDF Summarization — Intake',
      description: 'Send us the PDF(s) and how you want them summarized. No call needed.',
      fields: [
        { type: 'file', label: 'Upload: PDF(s) to summarize', required: true },
        {
          type: 'multipleChoice',
          label: 'Summary format',
          options: ['Bullet points', 'Paragraph', 'Executive summary'],
          required: true,
        },
        { type: 'text', label: 'Intended audience', required: false },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'Form Automation — Intake',
      description:
        'Send us your existing paper or PDF form and what you want it turned into. No call needed.',
      fields: [
        {
          type: 'file',
          label: 'Upload: existing paper or PDF form',
          required: true,
        },
        {
          type: 'multipleChoice',
          label: 'Desired output',
          options: ['Fillable PDF', 'Web form', 'Google Form'],
          required: true,
        },
        {
          type: 'multipleChoice',
          label: 'Integration needed on submit',
          options: ['Email', 'Sheets', 'CRM', 'None'],
          required: true,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'Content Generation — Intake',
      description:
        'Tell us what content you need and give us your brand voice guide. No call needed.',
      fields: [
        {
          type: 'text',
          label: 'Content type (article, guide, script, etc.)',
          required: true,
        },
        { type: 'paragraph', label: 'Topic list', required: true },
        { type: 'text', label: 'Word count / length', required: true },
        {
          type: 'file',
          label: 'Upload: brand voice guide (optional)',
          required: false,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
    {
      title: 'File Organization — Intake',
      description:
        'Give us access to the drive/folder and tell us the problem. No call needed.',
      fields: [
        {
          type: 'text',
          label: 'Link to the drive/folder to organize',
          required: true,
        },
        { type: 'paragraph', label: 'Current pain points', required: true },
        {
          type: 'paragraph',
          label: 'Desired folder structure (or write "recommend one")',
          required: false,
        },
        STANDARD_TURNAROUND,
        BUDGET,
      ],
    },
  ];
}
