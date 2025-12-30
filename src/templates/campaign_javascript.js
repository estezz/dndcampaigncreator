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
const textarea = document.getElementById("popupTextarea");
const submitEditBtn = document.getElementById("submitEdit");
const triggerBtns = document.getElementsByClassName("open-popup");

// Open modal on button click
document.querySelectorAll('[clickable]').forEach(item => {
    item.onclick = function () {
        modal.style.display = "block";
        // Display the ID of the clicked button
        textarea.value = this.id;
    }
});

// Close modal when (x) is clicked
submitEditBtn.onclick = function () {
    input = document.getElementById("popupTextarea").value;
    modal.style.display = "none";
    try {
        const response = fetch('/api/edit/campaign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/html'
            },
            body: input
        });

        if (!response.ok) {
            const errorMessage = response.text();
            throw new Error(errorMessage);
        }

        const responseData =  response.text();
            
        document.write( responseData );

    } catch (error) {
        console.error('Error submitting form:', error);
        output.innerHTML = `An error occurred: ${error.message}`;
    } finally {
        spinner.style.display = 'none';
    }
}

// Close modal if user clicks outside of it
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


