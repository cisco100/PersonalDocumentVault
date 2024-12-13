     $(document).ready(function() {
            $('#example').DataTable({
                responsive: true,
                pageLength: 5,
                language: {
                    search: "Search"
                },
                "bDestroy": true,
                buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print', 'colvis'
        ]
            });
        });
 

 








 // descriiption 

document.addEventListener('DOMContentLoaded', function() {
        // Description action
        document.querySelectorAll('.description-action').forEach(item => {
            item.addEventListener('click', event => {
                event.preventDefault();
                const folderId = event.target.getAttribute('data-folder-id');
                fetch(`/folders/${folderId}/description/`)
                    .then(response => response.json())
                    .then(data => {
                        Swal.fire({
                            title: 'Folder Description',
                            html: data.description,
                            icon: 'info'
                        });
                    });
            });
        });


 


  

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
    

    });


 
$(document).ready(function() {
    $('.delete-action').on('click', function(e) {
        e.preventDefault();
        const itemId = $(this).data('item-id');
        const itemType = $(this).data('item-type');
        handleDelete(itemId, itemType);
    });
});

function handleDelete(itemId, itemType) {
    Swal.fire({
        title: 'Delete Options',
        text: "Choose how you want to delete this item",
        icon: 'warning',
        showCancelButton: true,
        showDenyButton: true,
        confirmButtonColor: '#3085d6',
        denyButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Move to Trash',
        denyButtonText: 'Delete Permanently',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // Move to trash
            sendDeleteRequest(itemId, itemType, 'trash');
        } else if (result.isDenied) {
            // Delete permanently
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    sendDeleteRequest(itemId, itemType, 'delete');
                }
            });
        }
    });
}

function sendDeleteRequest(itemId, itemType, action) {
    $.ajax({
        url: '/delete-item/',
        type: 'POST',
        data: {
            item_id: itemId,
            item_type: itemType,
            action: action,
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        success: function(data) {
            if (data.status === 'success') {
                Swal.fire('Success', data.message, 'success').then(() => {
                    location.reload();
                });
            } else {
                Swal.fire('Error', data.message, 'error');
            }
        },
        error: function() {
            Swal.fire('Error', 'An error occurred while processing your request.', 'error');
        }
    });
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

