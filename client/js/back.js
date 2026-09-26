document.addEventListener('click',function(e){var t=e.target.closest?e.target.closest('[data-back]'):null;if(t){e.preventDefault();history.back();}});
