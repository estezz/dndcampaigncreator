const form = document.getElementById('adventure-form');
const spinner = document.getElementById('spinner');
const output = document.querySelector('.output');

form.addEventListener('submit', async function (event) {
    event.preventDefault();

    spinner.style.display = 'block';
    output.innerHTML = '';

    const formData = new FormData(form);
    const jsonData = Object.fromEntries(formData);
    const jsonString = JSON.stringify(jsonData);

    try {
        const response = await fetch('/api/generate/campaign', {
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
            
        document.write( responseData );

    } catch (error) {
        console.error('Error submitting form:', error);
        output.innerHTML = `An error occurred: ${error.message}`;
    } finally {
        spinner.style.display = 'none';
    }
});
