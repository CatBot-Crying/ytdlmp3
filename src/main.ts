import './style.css'; async function downloadMp3(): 
Promise<void> {
  const urlInput = 
  document.getElementById('youtubeUrl') as 
  HTMLInputElement; const resultElement = 
  document.getElementById('result') as 
  HTMLParagraphElement;
  
  const url = urlInput.value; if (!url) { 
    resultElement.innerText = 'Please enter a URL.'; 
    return;
  }
  resultElement.innerText = 'Processing...';
  
  try { const response = await 
    fetch(`/dl?url=${encodeURIComponent(url)}`); 
    const data: { link?: string } = await 
    response.json();
    
    if (data.link) { resultElement.innerHTML = `<a 
      href="${data.link}" 
      target="_blank">Download</a>`;
    } else {
      resultElement.innerText = 'Failed to get the 
      MP3 link.';
    }
  } catch (error) {
    resultElement.innerText = `Error: ${(error as 
    Error).message}`;
  }
}
// Add event listener when DOM is loaded
document.addEventListener('DOMContentLoaded', () => { 
  const downloadBtn = 
  document.getElementById('downloadBtn') as 
  HTMLButtonElement; 
  downloadBtn.addEventListener('click', downloadMp3);
});
