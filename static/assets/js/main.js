// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menu-toggle');
    const wrapper = document.getElementById('wrapper');
    const mainContent = document.getElementById('main-content');
    const links = document.querySelectorAll('.list-group-item[data-url]');

    menuToggle.addEventListener('click', function () {
        wrapper.classList.toggle('toggled');
    });

    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    mainContent.innerHTML = doc.querySelector('#main-content').innerHTML;
                    history.pushState(null, '', url);
                });
        });
    });
});

 

 // static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('create-folder-form');
    
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const url = form.action;
        const formData = new FormData(form);

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
        })
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newContent = doc.querySelector('#main-content').innerHTML;
            document.querySelector('#main-content').innerHTML = newContent;
            $('#addFolderModal').modal('hide');
        })
        .catch(error => console.error('Error:', error));
    });
});
