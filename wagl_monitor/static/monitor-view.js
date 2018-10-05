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
          column.footer().innerHTML = '<input class="column-search" type="text" placeholder="' + columnConfig[idx]['title'] + '" />';
        }
      });
      // Applies changes for every searchable column before calling draw
      $( 'input.column-search' ).on( 'keyup change', function(eventParams) {
        if (eventParams.which == 13 ) {
          eventParams.performSearch = false;
          table.columns().every( function(table, _, idx) {
            var column = this,
              columnInput = $('input.column-search', column.footer());
            if ( columnInput.val() !== undefined && column.search() !== columnInput.val()) {
              column.search(columnInput.val());
              eventParams.performSearch = true;
            }
          });
          if ( eventParams.performSearch ) {
            table.draw();
          }
        }
      })
    }
  });
  window.dev = table;
});
