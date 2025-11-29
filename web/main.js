const form = document.getElementById('adventure-form'); // Get your form element

form.addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(form); // Collect form data
    const jsonData = Object.fromEntries(formData); // Convert to plain object
    const jsonString = JSON.stringify(jsonData); // Convert to JSON string

    try {
        const response = await fetch('/api/generate/campaign', { // Replace with your API endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json' // Optional: Request JSON response
            },
            body: jsonString
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(errorMessage);
        }

        const responseData = await response.text(); // Parse JSON response
        console.log('Success:', responseData);
        document.documentElement.innerHTML = responseData;

    } catch (error) {
        console.error('Error submitting form:', error);
    }
});