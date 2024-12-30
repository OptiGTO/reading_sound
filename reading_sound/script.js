/*****************************************************
 * script.js 
 * 1) Single-page navigation for sidebar sections
 * 2) Sub-section navigation for home bulletin boards
 * 3) Other existing functionalities (random book, search, etc.)
 *****************************************************/

// 1. Random Book Data & Function
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

// 2. Search Functionality
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

// 3. Login / Membership Simulation (if needed)
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

// 4. Single-page navigation for the main sidebar
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

  // 5. Sub-section navigation (Home bulletin board)
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

// 6. Post submission spinner (if you have a new-post form on post.html)
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
