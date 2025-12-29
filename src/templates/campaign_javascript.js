
function downloadPartialHTML() {
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
}
