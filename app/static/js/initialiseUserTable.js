$(document).ready(function() {
    var users_js = $('#users').DataTable( {
        "processing": true,
        "ajax": {url:"/admin/users/get",
                dataSrc:""
                },
        // add column definitions to map your json to the table                                           
        "columns": [
            {data: "id"},
            {data: "name", render: $.fn.dataTable.render.text()},
            {data: "organisation", render: $.fn.dataTable.render.text()},
            {data: "username", render: $.fn.dataTable.render.text()},
            {data: "email", render: $.fn.dataTable.render.text()},
            {data: "lastSeen"},
            {data: "admin"},
            {data: "reviewer"},
            {targets: -1, data: null, defaultContent: "<a class='edit-user'>Edit</a>"}
        ],
        fixedHeader: {
            headerOffset: $('#outer-navbar').outerHeight()
        },
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
        ],
        initComplete: function(settings, json) {
            var user_table = document.getElementById("users");
            for (var i = 1, row; row = user_table.rows[i]; i++) {
                var a = row.cells[8].getElementsByTagName('a');
                a[0].href = "user/" + row.cells[3].textContent + "/edit";
            };
        }
    });
    new $.fn.dataTable.FixedHeader( users_js, {
        "offsetTop": $('#outer-navbar .navbar').height()
    });
});