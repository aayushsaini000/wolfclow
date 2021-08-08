// Call the dataTables jQuery plugin
$(document).ready(function() {
    $('#userListTable').DataTable( {
        "ajax": '../ajax/data/arrays.txt'
    } );
});
  