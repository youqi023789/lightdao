document.addEventListener('click',function(e){var t=e.target.closest?e.target.closest('[data-go]'):null;if(t){var u=t.getAttribute('data-go');if(u)location.href=u;}});
