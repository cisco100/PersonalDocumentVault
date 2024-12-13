 // This script should be included at the end of your body tag or use defer attribute if in head

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const decryptLinks = document.querySelectorAll('.rename-action');
    console.log('Found decrypt links:', decryptLinks.length);

    decryptLinks.forEach(link => {
        console.log('Adding event listener to:', link);
        link.addEventListener('click', function(e) {
            console.log('Decrypt link clicked');
            e.preventDefault();
            const fileId = this.dataset.fileId;
            console.log('File ID:', fileId);

            Swal.fire({
                title: 'Enter Private Key',
                input: 'password',
                inputAttributes: {
                    autocapitalize: 'off'
                },
                showCancelButton: true,
                confirmButtonText: 'Submit',
                showLoaderOnConfirm: true,
                preConfirm: (key) => {
                    console.log('Sending decrypt request');
                    return fetch('/decrypt/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ key: key, file_id: fileId })
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(response.statusText)
                        }
                        return response.json()
                    })
                    .catch(error => {
                        Swal.showValidationMessage(
                            `Request failed: ${error}`
                        )
                    })
                },
                allowOutsideClick: () => !Swal.isLoading()
            }).then((result) => {
                if (result.isConfirmed) {
                    console.log('Decryption successful');
                    Swal.fire({
                        title: 'Decryption Successful',
                        icon: 'success',
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        Swal.fire({
                            title: 'What would you like to do?',
                            showDenyButton: true,
                            showCancelButton: true,
                            confirmButtonText: 'Share',
                            denyButtonText: 'Download',
                        }).then((result) => {
                            if (result.isConfirmed) {
                                console.log('Sharing file');
                                window.location.href = `/share/${fileId}/`;
                            } else if (result.isDenied) {
                                console.log('Downloading file');
                                window.location.href = `/download/${fileId}/`;
                            }
                        })
                    })
                }
            })
        });
    });
});

// Function to get CSRF token
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

console.log('Script loaded');