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
// adminGeneratedBooks 배열: 관리자 측에서 미리 선정한 책 목록

const randomBookBtn = document.getElementById("random-book-btn");
const randomBookContainer = document.getElementById("random-book-container");

function getRandomBook() {
  // 무작위 책을 선택해 화면에 표시하는 함수
  const randomIndex = Math.floor(Math.random() * adminGeneratedBooks.length);
  // 0부터 배열 길이-1 범위 내 무작위 정수 생성
  const book = adminGeneratedBooks[randomIndex];
  // 무작위 인덱스로 책 객체를 가져옴

  randomBookContainer.innerHTML = `
    <p><strong>Title:</strong> ${book.title}</p>
    <p><strong>Author:</strong> ${book.author}</p>
    <p><strong>Genre:</strong> ${book.genre}</p>
  `;
  // 무작위로 선택된 책의 정보(제목, 저자, 장르)를 HTML로 삽입
}

if (randomBookBtn) {
  randomBookBtn.addEventListener("click", getRandomBook);
}
// 버튼이 실제로 존재한다면, 클릭 시 getRandomBook 함수를 실행

// 2. 검색 기능
const searchBtn = document.getElementById("search-btn");
const searchInput = document.getElementById("search-input");

// CSRF 토큰 설정 추가                                                    // Django CSRF 보호를 위한 설정
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// fetch 요청에 사용할 기본 헤더 설정
const fetchHeaders = {
    'X-CSRFToken': csrftoken,
    'Content-Type': 'application/json',
};

// API 요청 함수 수정
async function searchPosts() {
    const query = searchInput.value.toLowerCase();
    try {
        const response = await fetch('/api/search/', {                    // Django URL 패턴에 맞는 엔드포인트
            method: 'POST',
            headers: fetchHeaders,
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        // 결과 처리
    } catch (error) {
        console.error('검색 중 오류 발생:', error);
    }
}

if (searchBtn) {
  searchBtn.addEventListener("click", searchPosts);
}
// 검색 버튼이 존재한다면, 클릭 시 searchPosts 실행

// 3. 로그인 시뮬레이션
const loginBtn = document.getElementById("login-btn");
const userNicknameEl = document.getElementById("user-nickname");

function loginUser() {
  // 로그인 시 유저 닉네임을 변경하는 예시 함수
  userNicknameEl.textContent = "BookLover99";
  console.log("User logged in as BookLover99.");
}

// 아래 주석을 해제하면, 실제로 해당 버튼을 클릭할 때 로그인 동작이 수행됨.
// if (loginBtn && userNicknameEl) {
//   loginBtn.addEventListener("click", loginUser);
// }

// 4. 메인 사이드바 네비게이션
document.addEventListener("DOMContentLoaded", () => {
  // DOM이 로드된 후에 실행
  const navLinks = document.querySelectorAll(".nav-link");
  const allSections = document.querySelectorAll(".section");

  // 초기 상태 설정 - 첫 번째 섹션을 기본으로 표시                          // 페이지 로드 시 첫 섹션 표시
  if (allSections.length > 0) {
    allSections[0].classList.add("active");
    if (navLinks.length > 0) {
      navLinks[0].classList.add("active");
    }
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetSectionId = link.getAttribute("data-section");

      // 모든 섹션과 링크의 active 클래스 제거
      allSections.forEach((section) => section.classList.remove("active"));
      navLinks.forEach((navLink) => navLink.classList.remove("active"));

      // 선택된 섹션과 링크만 active 클래스 추가
      const targetSection = document.getElementById(targetSectionId);
      if (targetSection) {
        targetSection.classList.add("active");
        link.classList.add("active");
      }
    });
  });

  // 5. 홈 게시판의 서브섹션 네비게이션
  const subLinks = document.querySelectorAll(".sub-link");
  const subSections = document.querySelectorAll(".sub-section");

  subLinks.forEach((subLink) => {
    subLink.addEventListener("click", (event) => {
      event.preventDefault();
      const targetSubId = subLink.getAttribute("data-subsection");

      // 모든 서브섹션 숨김
      subSections.forEach((subSec) => {
        subSec.classList.remove("active");
      });

      // 클릭된 서브링크에 해당하는 서브섹션만 표시
      const targetSubSection = document.getElementById(targetSubId);
      if (targetSubSection) {
        targetSubSection.classList.add("active");
      }

      // 활성 서브링크 스타일 업데이트
      subLinks.forEach((btn) => btn.classList.remove("active"));
      subLink.classList.add("active");
    });
  });

  // 섹션 전환 이벤트
  document.querySelectorAll('.nav-menu .nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      // 모든 섹션에서 active 클래스 제거
      document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
      });
      
      // 클릭된 링크에 해당하는 섹션 활성화
      const targetId = link.dataset.section;
      const targetSection = document.getElementById(targetId);
      targetSection.classList.add('active');
      
      // 섹션이 변경될 때마다 무조건 전체 서브섹션으로 초기화
      if (targetId === 'home-section') {
        resetToDefaultSubsection(targetSection, 'home-full-board');
      } 
      else if (targetId === 'post-section') {
        resetToDefaultSubsection(targetSection, 'post-full-board');
      }
    });
  });

  // 새로운 초기화 함수
  function resetToDefaultSubsection(section, defaultSubsectionId) {
    // 모든 서브섹션 비활성화
    section.querySelectorAll('.sub-section').forEach(sub => {
      sub.classList.remove('active');
    });
    
    // 모든 서브링크 버튼 비활성화
    section.querySelectorAll('.sub-link').forEach(btn => {
      btn.classList.remove('active');
    });
    
    // 전체 서브섹션 활성화
    const defaultSubsection = section.querySelector(`#${defaultSubsectionId}`);
    if (defaultSubsection) {
      defaultSubsection.classList.add('active');
    }
    
    // 전체 버튼 활성화
    const defaultButton = section.querySelector(`.sub-link[data-subsection="${defaultSubsectionId}"]`);
    if (defaultButton) {
      defaultButton.classList.add('active');
    }
  }
});

// 6. 게시글 작성 시 로딩 효과
const newPostForm = document.getElementById("new-post-form");
const submitSpinner = document.getElementById("submit-spinner");

// 새 게시글 제출 함수 수정
async function handleNewPostSubmit(event) {
    event.preventDefault();
    if (submitSpinner) {
        submitSpinner.style.display = "inline-block";
    }

    try {
        const formData = new FormData(newPostForm);                     // 폼 데이터 수집
        const response = await fetch('/api/posts/create/', {            // Django URL 패턴에 맞는 엔드포인트
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        });

        if (response.ok) {
            alert("게시글이 등록되었습니다!");
            newPostForm.reset();
        } else {
            alert("게시글 등록에 실패했습니다.");
        }
    } catch (error) {
        console.error('게시글 등록 중 오류:', error);
        alert("오류가 발생했습니다.");
    } finally {
        if (submitSpinner) {
            submitSpinner.style.display = "none";
        }
    }
}

if (newPostForm) {
  newPostForm.addEventListener("submit", handleNewPostSubmit);
}

// 7. Google Books API 연동 (책 이미지 검색 예시)
async function searchBookImage(title, author) {
  try {
    const query = `${title} ${author}`.replace(/ /g, '+');
    // 책 제목과 저자를 합쳐 검색 쿼리 만듦. 공백은 '+'로 대체
    const response = await fetch(
      `https://www.googleapis.com/books/v1/volumes?q=${query}&maxResults=1`
    );
    // 구글 북스 API에 요청
    const data = await response.json();
    
    if (data.items && data.items[0].volumeInfo.imageLinks) {
      return data.items[0].volumeInfo.imageLinks.thumbnail;
    }
    // 썸네일 이미지 링크가 있으면 반환
    return null;
  } catch (error) {
    console.error('책 이미지 검색 중 오류:', error);
    return null;
  }
}

// 8. 게시글 카드 생성
async function createPostCard(postData) {
  // 비동기로 구글 북스 API 썸네일 요청
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
  // 생성된 HTML 문자열을 반환
}



// 사이드바 축소 기능 추가
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.querySelector('.sidebar');
  let isCollapsed = false;

  // 윈도우 크기 변경에 따라 사이드바 자동 축소
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 1200 && !isCollapsed) {
      sidebar.classList.add('collapsed');
      isCollapsed = true;
    } else if (window.innerWidth > 1200 && isCollapsed) {
      sidebar.classList.remove('collapsed');
      isCollapsed = false;
    }
  });

  // 사이드바에 마우스를 올리면 다시 펴지고, 떠나면 접힘
  sidebar.addEventListener('mouseenter', () => {
    if (isCollapsed) {
      sidebar.classList.remove('collapsed');
    }
  });

  sidebar.addEventListener('mouseleave', () => {
    if (isCollapsed) {
      sidebar.classList.add('collapsed');
    }
  });
});

// 서브섹션 버튼 클릭 이벤트 처리
document.querySelectorAll('.sub-link').forEach(button => {
  button.addEventListener('click', () => {
    const section = button.closest('.section'); // 현재 섹션 찾기
    
    // 현재 섹션 내의 모든 서브섹션 버튼에서 active 제거
    section.querySelectorAll('.sub-link').forEach(btn => {
      btn.classList.remove('active');
    });
    
    // 클릭된 버튼 활성화
    button.classList.add('active');
    
    // 모든 서브섹션 숨기기
    section.querySelectorAll('.sub-section').forEach(sub => {
      sub.classList.remove('active');
    });
    
    // 선택된 서브섹션 표시
    const targetId = button.dataset.subsection;
    section.querySelector(`#${targetId}`).classList.add('active');
  });
});
