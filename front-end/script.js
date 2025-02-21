document.getElementById('download-button').addEventListener('click', function() {
    // Simulate starting a file download
    const downloadLink = document.createElement('a');
    downloadLink.href = 'http://localhost/Jogo.zip'
    downloadLink.download = 'Jogo.zip';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    // Show extra info after the download starts
    document.getElementById('extra-info').classList.remove('hidden');
});
