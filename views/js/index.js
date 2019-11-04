import * as FilePond from 'filepond';

// Create a multi file upload component
const pond = FilePond.create({
    multiple: true,
    name: 'filepond'
});

// Add it to the DOM
document.body.appendChild(pond.element);