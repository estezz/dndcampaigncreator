document.getElementById("download-button").addEventListener('click', function () {
    // 1. Get the content of the target element
    const content = document.getElementById('content-to-download').innerHTML;

    // 2. Create a blob from the HTML content
    const blob = new Blob([content], { type: 'text/html' });

    // 3. Create a temporary anchor element
    const a = document.createElement('a');
    a.download = "{{title | escape}}.html"; // Set the filename
    a.href = URL.createObjectURL(blob);

    // 4. Trigger the download
    a.click();

    // 5. Clean up
    URL.revokeObjectURL(a.href);
});

// Get DOM elements
const modal = document.getElementById("myModal");
const editForm = document.getElementById("editForm")
const elementID = document.getElementById("elementID");
const submitEditBtn = document.getElementById("submitEdit");
const triggerBtns = document.getElementsByClassName("open-popup");

// Open modal on button click
document.querySelectorAll('[clickable]').forEach(item => {
    item.onclick = function () {
        modal.style.display = "block";
        // Display the ID of the clicked button
        elementID.value = this.id;
    }
});

submitEditBtn.addEventListener ('click', async function (event) {
    event.preventDefault();

    // const formData = new FormData(editForm);
    // const jsonData = Object.fromEntries(formData);
    // const jsonString = JSON.stringify(jsonData);
    
    const jsonData = {
        "elementID" : elementID.value,
        "prompt" : document.getElementById("prompt").value,
    }
    const jsonString = JSON.stringify(jsonData);

    try {
        const response = await fetch('/api/edit/campaign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/html'
            },
            body: jsonString
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(errorMessage);
        }

        const responseData = await response.text();
        output.innerHTML = '';
        document.write( responseData );

    } catch (error) {
        console.error('Error submitting form:', error);
        output.innerHTML = `An error occurred: ${error.message}`;
    } finally {
       
    }
});

// Close modal if user clicks outside of it
// window.onclick = function (event) {
//     if (event.target == modal) {
//         modal.style.display = "none";
//     }
// }


