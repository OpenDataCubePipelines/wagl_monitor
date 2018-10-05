function renderItemLink(data, type, row, meta) {
  return (
    '<a href="/dt/WaglBatchItem/batch_id/' + data + '/">'
    + 'Item View &#8618;</a>'
  );
}

var columnConfig = [
  {"title": "Submit User", "data": "user"},
  {"title": "Batch ID", "data": "group_id"},
  {
    "title": "Submit Time",
    "data": "submit_time", 
    "type": "date", 
    "searchable": false
  },
  {
    "title": "Item View",
    "data": "id",
    "type": "html",
    "searchable": false,
    "render": renderItemLink
  },
  //{"title": "Summary", "data": "summary", "visible": false}
];
