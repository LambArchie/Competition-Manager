$(document).ready(function() {
    $('#users').DataTable( {
        "processing": true,
        "ajax": {url:"/admin/users/get",
                dataSrc:""
                },
        // add column definitions to map your json to the table                                           
        "columns": [
            {data: "id"},
            {data: "name"},
            {data: "organisation"},
            {data: "username"},
            {data: "email"},
            {data: "lastSeen"},
            {data: "admin"},
            {data: "reviewer"}
        ],
        // export
        //dom: 'lfrtipB',
        dom: "<'row'<'col-sm-12 col-md-auto'l><'col-sm-12 col-md-3 mr-auto'B><'col-sm-12 col-md-auto'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        buttons: [
            //'csv', 'excel', 'pdf', 'print'
            { extend: 'csv', className: 'btn-sm'},
            { extend: 'excel', className: 'btn-sm'},
            { extend: 'pdf', className: 'btn-sm'},
            { extend: 'print', className: 'btn-sm'}
        ]
    } );
});