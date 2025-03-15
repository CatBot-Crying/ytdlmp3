document.addEventListener('DOMContentLoaded', () => {
  const downloadBtn = document.getElementById('downloadBtn');
  
  async function downloadMp3() {
    const url = document.getElementById('youtubeUrl').value;
    const resultElement = document.getElementById('result');
    
    if (!url) {
      resultElement.innerText = 'Please enter a URL.';
      return;
    }
    
    resultElement.innerText = 'Processing...';
    
    try {
      const response = await fetch(`http://ec2-3-26-101-127.ap-southeast-2.compute.amazonaws.com:3000/dl?url=${encodeURIComponent(url)}`);
      const data = await response.json();
      
      if (data.link) {
        resultElement.innerHTML = `<a href="${data.link}" target="_blank">Download</a>`;
      } else {
        resultElement.innerText = 'Failed to get the MP3 link.';
      }
    } catch (error) {
      resultElement.innerText = 'Error: ' + error.message;
    }
  }

  downloadBtn.addEventListener('click', downloadMp3);
});
