var columnConfig = [
  {"title": "Granule ID", "data": "granule"},
  {"title": "Source Package", "data": "level1"},
  {
    "title": "Status",
    "data": "processing_status",
  },
  {
    "title": "Job ID", 
    "data": "job_group_id",
    "visible": false,
  },
  {
    "title": "Batch ID",
    "data": "batch_group_id",
    "visible": false,
  },
  {"title": "Failed Task", "data": "failed_task"},
  {"title": "Exception", "data": "exception"},
  {
    "title": "Error Log",
    "data": "error_log",
    "visible": false
  },
  {
    "title": "Error Time",
    "data": "error_ts",
    "searchable": false,
    "visible": false
  }
];
