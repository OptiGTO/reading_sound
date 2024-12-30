/*****************************************************
 * script.js 
 * 1) Single-page navigation for sidebar sections
 * 2) Sub-section navigation for home bulletin boards
 * 3) Other existing functionalities (random book, search, etc.)
 *****************************************************/

// 1. 무작위 책 추천 기능
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

// 2. 검색 기능
const searchBtn = document.getElementById("search-btn");
const searchInput = document.getElementById("search-input");

function searchPosts() {
  const query = searchInput.value.toLowerCase();
  console.log("Searching for posts with query:", query);
  // ... any filtering logic
}

if (searchBtn) {
  searchBtn.addEventListener("click", searchPosts);
}

// 3. 로그인 시뮬레이션
const loginBtn = document.getElementById("login-btn");
const userNicknameEl = document.getElementById("user-nickname");

function loginUser() {
  userNicknameEl.textContent = "BookLover99";
  console.log("User logged in as BookLover99.");
}

// If we want the login button to do something (otherwise, it just links to login.html)
if (loginBtn && userNicknameEl) {
  // loginBtn.addEventListener("click", loginUser);
}

// 4. 메인 사이드바 네비게이션
document.addEventListener("DOMContentLoaded", () => {
  const navLinks = document.querySelectorAll(".nav-link");
  const allSections = document.querySelectorAll(".section");

  navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const targetSectionId = link.getAttribute("data-section");

      // Hide all main sections
      allSections.forEach((section) => {
        section.classList.remove("active");
      });

      // Show the chosen main section
      const targetSection = document.getElementById(targetSectionId);
      if (targetSection) {
        targetSection.classList.add("active");
      }

      // Update active link style
      navLinks.forEach((otherLink) => otherLink.classList.remove("active"));
      link.classList.add("active");
    });
  });

  // 5. 홈 게시판의 서브섹션 네비게이션
  const subLinks = document.querySelectorAll(".sub-link");
  const subSections = document.querySelectorAll(".sub-section");

  subLinks.forEach((subLink) => {
    subLink.addEventListener("click", (event) => {
      event.preventDefault();
      const targetSubId = subLink.getAttribute("data-subsection");

      // Hide all sub-sections
      subSections.forEach((subSec) => {
        subSec.classList.remove("active");
      });

      // Show the chosen sub-section
      const targetSubSection = document.getElementById(targetSubId);
      if (targetSubSection) {
        targetSubSection.classList.add("active");
      }

      // Update active style on sub-link buttons
      subLinks.forEach((btn) => btn.classList.remove("active"));
      subLink.classList.add("active");
    });
  });
});

// 6. 게시글 작성 시 로딩 효과
const newPostForm = document.getElementById("new-post-form");
const submitSpinner = document.getElementById("submit-spinner");

function handleNewPostSubmit(event) {
  event.preventDefault();
  if (submitSpinner) {
    submitSpinner.style.display = "inline-block";
  }
  setTimeout(() => {
    if (submitSpinner) {
      submitSpinner.style.display = "none";
    }
    alert("Your post has been published!");
    newPostForm.reset();
  }, 2000);
}

if (newPostForm) {
  newPostForm.addEventListener("submit", handleNewPostSubmit);
}

// 7. Google Books API 연동
async function searchBookImage(title, author) {
  try {
    const query = `${title} ${author}`.replace(/ /g, '+');
    const response = await fetch(
      `https://www.googleapis.com/books/v1/volumes?q=${query}&maxResults=1`
    );
    const data = await response.json();
    
    if (data.items && data.items[0].volumeInfo.imageLinks) {
      return data.items[0].volumeInfo.imageLinks.thumbnail;
    }
    return null;
  } catch (error) {
    console.error('책 이미지 검색 중 오류:', error);
    return null;
  }
}

// 8. 게시글 카드 생성
async function createPostCard(postData) {
  const bookImage = await searchBookImage(postData.title, postData.author);
  
  return `
    <article class="post-card hover-effect">
      <div class="post-card-content">
        ${bookImage ? 
          `<div class="book-image">
            <img src="${bookImage}" alt="${postData.title} 표지" />
           </div>` 
          : ''
        }
        <h3 class="post-title">${postData.title}</h3>
        <p class="post-author"><strong>저자:</strong> ${postData.author}</p>
        <p class="post-genre"><strong>장르:</strong> ${postData.genre}</p>
        <p class="post-stats">
          <span><strong>조회수:</strong> ${postData.views || 0}</span> | 
          <span><strong>추천:</strong> ${postData.likes || 0}</span> | 
          <span><strong>댓글:</strong> ${postData.comments || 0}</span>
        </p>
        <p class="post-excerpt">${postData.excerpt || '내용이 없습니다...'}</p>
        <button class="btn hover-effect">게시글 보기</button>
      </div>
    </article>
  `;
}

// 9. 게시글 로드
async function loadPosts(boardId) {
  const samplePosts = [
    {
      title: "1984",
      author: "George Orwell",
      genre: "소설",
      excerpt: "디스토피아 세계를 그린 조지 오웰의 대표작..."
    },
    // 더 많은 게시글 데이터...
  ];

  const postsContainer = document.querySelector(`#${boardId} .post-list`);
  if (!postsContainer) return;

  postsContainer.innerHTML = ''; // 기존 게시글 비우기
  
  // 각 게시글에 대해 카드 생성 및 추가
  for (const post of samplePosts) {
    const postCardHTML = await createPostCard(post);
    postsContainer.insertAdjacentHTML('beforeend', postCardHTML);
  }
}
