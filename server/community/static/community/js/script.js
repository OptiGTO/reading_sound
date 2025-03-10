// File: community/static/community/js/script.js

/*****************************************************
 * 현재 js 파일 로드 되지 않음
 * script.js 
 * 1. Random Book Recommendation
 * 2. Sub-section Navigation (Home & Post sections only)
 * 3. Form Handling
 * 
 *****************************************************/

// 1. Random Book Recommendation Functionality
const adminGeneratedBooks = [
  { title: "1984", author: "George Orwell", genre: "Dystopian" },
  { title: "To Kill A Mockingbird", author: "Harper Lee", genre: "Classic" },
  { title: "The Great Gatsby", author: "F. Scott Fitzgerald", genre: "Classic" },
  { title: "Pride and Prejudice", author: "Jane Austen", genre: "Romance" },
  { title: "Fahrenheit 451", author: "Ray Bradbury", genre: "Sci-Fi" },
];

const randomBookBtn = document.getElementById("random-book-btn");
const randomBookContainer = document.getElementById("random-book-container");

function getRandomBook() {
  const randomIndex = Math.floor(Math.random() * adminGeneratedBooks.length);
  const book = adminGeneratedBooks[randomIndex];
  randomBookContainer.innerHTML = `
    <p><strong>Title:</strong> ${book.title}</p>
    <p><strong>Author:</strong> ${book.author}</p>
    <p><strong>Genre:</strong> ${book.genre}</p>
  `;
}

if (randomBookBtn) {
  randomBookBtn.addEventListener("click", getRandomBook);
}

// 2. Sub-section Navigation (Only for Home & Post sections)
document.querySelectorAll('.sub-link').forEach(button => {
  button.addEventListener('click', (e) => {
    e.preventDefault();
    
    // 현재 활성화된 버튼과 섹션 비활성화
    const parentSection = button.closest('.section');
    parentSection.querySelectorAll('.sub-link.active').forEach(btn => btn.classList.remove('active'));
    parentSection.querySelectorAll('.sub-section.active').forEach(section => section.classList.remove('active'));
    
    // 새로 선택된 요소 활성화
    button.classList.add('active');
    const targetId = button.dataset.subsection;
    parentSection.querySelector(`#${targetId}`).classList.add('active');
  });
});




// 3. CSRF Token Handling & Form Submission
let csrftoken;
const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
if (tokenElement) {
  csrftoken = tokenElement.value;
}



// 4. Mobile Submenu Toggle
document.addEventListener('DOMContentLoaded', () => {
  const submenuParent = document.querySelector('.has-submenu');
  
  if (submenuParent && window.innerWidth <= 768) {
    submenuParent.addEventListener('click', (e) => {
      e.preventDefault();
      submenuParent.querySelector('.submenu').classList.toggle('active');
    });
  }
});

// 5. Error Handling for Images
document.querySelectorAll('img').forEach(img => {
  img.addEventListener('error', (e) => {
    e.target.src = '{% static "community/images/no-image.png" %}';
    e.target.alt = 'Image not available';
  });
});












/*



document.querySelector('form').addEventListener('submit', function(e) {
  // 캐시 방지 파라미터 추가
  const timestamp = new Date().getTime();
  window.location.href = `{% url 'community:home' %}?nocache=${timestamp}`;
});
*/


// Generic form handler
/*
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', async (event) => {
    //event.preventDefault();
    
    try {
      const formData = new FormData(form);
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken
        },
        body: formData
      });

      if (response.ok) {
        window.location.reload(); // Refresh after successful submission
      } else {
        alert('Form submission failed');
      }
    } catch (error) {
      console.error('Submission error:', error);
      alert('An error occurred');
    }
  });
});
*/