// Render the data table
$(document).ready(function() {
  (function() {
    // Init table footer
    var foot_tr = $('table.processing-results tfoot tr'),
      i = 0;
    for(i=0; i<columnConfig.length; i+=1) {
      foot_tr.append( $('<th></th>') );
    }
  })();
  var table = $('.processing-results').DataTable({
    "sDom": "Brtipl",
    "pageLength": 25,
    "processing": true,
    "serverSide": true,
    "ajax": apiEndpoint,
    buttons: [{"extend": "colvis", "columns": ":not(.noVis)"}],
    columns: columnConfig,
    initComplete: function(settings, json) {
      var table = settings.oInstance.api();
      table.columns().every( function(table, _, idx) {
        var column = this;
        // Only add search field for searchable columns
        if ( columnConfig[idx].searchable !== false ) {
          column.footer().innerHTML = '<input type="text" placeholder="' + columnConfig[idx]['title'] + '" />';

          $( 'input', this.footer() ).on( 'keyup change', function(event) {
            // Only search on enter keypress
            if( event.which == 13 && column.search() !== this.value ) {
              column.search(this.value).draw();
            }
          });
        }
      });
    }
  });
  window.dev = table;
});
