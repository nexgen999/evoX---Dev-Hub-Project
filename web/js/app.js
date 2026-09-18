let globalData = {
  profile: {},
  categories: [],
  projects: [],
  socials: [],
  githubRepos: [],
  githubStars: []
};

let activeMode = 'home'; // 'home', 'repos', 'stars'
let activeCategory = 'all';
let isListView = false;
let currentSort = 'default';

const DEFAULT_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%231e293b'/><text x='50%' y='50%' font-size='30' fill='%2394a3b8' text-anchor='middle' dy='.3em'>👤</text></svg>";
const DEFAULT_BANNER = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='180' viewBox='0 0 300 180'><rect width='300' height='180' fill='%231e293b'/><text x='50%' y='50%' font-size='40' fill='%23334155' text-anchor='middle' dy='.3em'>📁</text></svg>";

document.addEventListener('DOMContentLoaded', async () => {
  await loadAllData();
  await fetchGitHubUserStats();
  renderProfile();
  renderSocials();
  renderCategories();
  renderContent();
  setupEvents();
});

async function loadAllData() {
  try {
    const [profileRes, catsRes, projsRes, socialsRes] = await Promise.all([
      fetch('web/config/profile.json'),
      fetch('web/config/categories.json'),
      fetch('web/config/projects.json'),
      fetch('web/config/socials.json')
    ]);

    globalData.profile = await profileRes.json();
    globalData.categories = await catsRes.json();
    globalData.projects = await projsRes.json();
    globalData.socials = await socialsRes.json();
  } catch (err) {
    console.error("Erreur de chargement des fichiers JSON :", err);
  }
}

// Fonction générique pour récupérer l'ensemble des pages de l'API GitHub
async function fetchAllGitHubPages(endpoint) {
  let results = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    try {
      const res = await fetch(`${endpoint}?per_page=100&page=${page}`);
      if (!res.ok) break;
      const data = await res.json();
      if (data.length === 0) {
        hasMore = false;
      } else {
        results = results.concat(data);
        page++;
        if (data.length < 100) hasMore = false;
      }
    } catch (e) {
      console.error("Erreur lors de la récupération paginée :", e);
      hasMore = false;
    }
  }
  return results;
}

async function fetchGitHubUserStats() {
  const username = globalData.profile.handle || 'nexgen999';
  try {
    const userRes = await fetch(`https://api.github.com/users/${username}`);
    if (userRes.ok) {
      const userData = await userRes.json();
      globalData.profile.stats = {
        repos: userData.public_repos,
        followers: userData.followers
      };
      if (!globalData.profile.avatar) globalData.profile.avatar = userData.avatar_url;
    }

    // Récupération complète sans limite de 100
    const [repos, stars] = await Promise.all([
      fetchAllGitHubPages(`https://api.github.com/users/${username}/repos`),
      fetchAllGitHubPages(`https://api.github.com/users/${username}/starred`)
    ]);

    globalData.githubRepos = repos;
    globalData.githubStars = stars;

  } catch (e) {
    console.warn("Erreur chargement GitHub :", e);
  }
}

function renderProfile() {
  const p = globalData.profile;
  document.getElementById('profile-avatar').src = p.avatar || DEFAULT_AVATAR;
  document.getElementById('profile-name').textContent = p.username || 'nexgen999';
  document.getElementById('profile-handle').textContent = `@${p.handle || 'nexgen999'}`;
  document.getElementById('profile-bio').textContent = p.bio || '';

  document.getElementById('stat-repos').textContent = p.stats?.repos ?? globalData.githubRepos.length;
  document.getElementById('stat-followers').textContent = p.stats?.followers ?? 0;
}

function renderSocials() {
  const container = document.getElementById('socials-container');
  if (!container) return;
  container.innerHTML = globalData.socials.map(s => `
    <a href="${s.url}" target="_blank" class="social-icon" title="${s.name}">
      <i class="${s.icon}"></i>
    </a>
  `).join('');
}

function renderCategories() {
  const sideContainer = document.getElementById('categories-list');
  if (!sideContainer) return;

  sideContainer.innerHTML = globalData.categories.map(c => {
    const count = globalData.projects.filter(p => p.category === c.id || c.id === 'all').length;
    const isActive = (c.id === activeCategory && activeMode === 'home') ? 'active-cat' : '';
    return `
      <div class="sidebar-cat-item ${isActive}" onclick="filterCategory('${c.id}')">
        <span><i class="${c.icon}"></i> ${c.name}</span>
        <span class="cat-count">${count}</span>
      </div>
    `;
  }).join('');
}

function renderContent() {
  const query = document.getElementById('search-input')?.value || '';
  if (activeMode === 'home') {
    renderProjects(query);
  } else if (activeMode === 'repos') {
    renderGitHubList(globalData.githubRepos, "Mes Repositories", query);
  } else if (activeMode === 'stars') {
    renderGitHubList(globalData.githubStars, "Mes Stars GitHub", query);
  }
}

function applySorting(items) {
  let list = [...items];
  if (currentSort === 'name-asc') {
    list.sort((a, b) => (a.title || a.name || '').localeCompare(b.title || b.name || ''));
  } else if (currentSort === 'name-desc') {
    list.sort((a, b) => (b.title || b.name || '').localeCompare(a.title || a.name || ''));
  } else if (currentSort === 'owner-asc') {
    list.sort((a, b) => {
      const ownerA = a.owner?.login || '';
      const ownerB = b.owner?.login || '';
      return ownerA.localeCompare(ownerB);
    });
  } else if (currentSort === 'stars-desc') {
    list.sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0));
  }
  return list;
}

function renderProjects(searchQuery = '') {
  const container = document.getElementById('projects-container');
  if (!container) return;
  container.innerHTML = '';

  const filteredCategories = activeCategory === 'all' 
    ? globalData.categories.filter(c => c.id !== 'all')
    : globalData.categories.filter(c => c.id === activeCategory);

  filteredCategories.forEach(cat => {
    let catProjs = globalData.projects.filter(p => p.category === cat.id);

    if (searchQuery) {
      catProjs = catProjs.filter(p => 
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
        (p.tags && p.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase())))
      );
    }

    catProjs = applySorting(catProjs);
    if (catProjs.length === 0) return;

    const section = document.createElement('div');
    section.className = 'category-section';
    const gridClass = isListView ? 'cards-list' : 'cards-grid';

    const cardsHtml = catProjs.map(p => {
      const imgSrc = (p.images && p.images.length > 0) ? p.images[0] : DEFAULT_BANNER;
      const tagsHtml = (p.tags || []).map(t => `<span class="tag">#${t}</span>`).join('');
      
      return `
        <div class="card ${isListView ? 'card-horizontal' : ''}">
          <img src="${imgSrc}" class="card-img" alt="${p.title}" onerror="this.src='${DEFAULT_BANNER}'">
          <div class="card-content">
            <h3 class="card-title" onclick="openProjectModal('${p.id}')">${p.title}</h3>
            <p class="card-desc">${p.description || ''}</p>
            <div class="card-tags">${tagsHtml}</div>
            <div class="card-footer">
              ${p.github ? `<a href="${p.github}" target="_blank" class="card-btn"><i class="fa-brands fa-github"></i> Dépôt</a>` : ''}
              ${p.demo ? `<a href="${p.demo}" target="_blank" class="card-btn"><i class="fa-solid fa-arrow-up-right-from-square"></i> Site Web</a>` : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');

    section.innerHTML = `
      <h2 class="category-header-title"><i class="${cat.icon}"></i> ${cat.name}</h2>
      <div class="${gridClass}">${cardsHtml}</div>
    `;
    container.appendChild(section);
  });
}

function renderGitHubList(items, title, searchQuery = '') {
  const container = document.getElementById('projects-container');
  if (!container) return;
  container.innerHTML = '';

  let filtered = items;
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    filtered = items.filter(i => 
      i.name.toLowerCase().includes(q) ||
      (i.owner && i.owner.login.toLowerCase().includes(q)) ||
      (i.description && i.description.toLowerCase().includes(q))
    );
  }

  filtered = applySorting(filtered);

  const section = document.createElement('div');
  section.className = 'category-section';
  const gridClass = isListView ? 'cards-list' : 'cards-grid';

  const cardsHtml = filtered.map(item => `
    <div class="card ${isListView ? 'card-horizontal' : ''}">
      <div class="card-content">
        <div class="card-header-gh">
          <h3 class="card-title-gh" onclick="openGitHubModal('${item.owner.login}', '${item.name}')">
            ${item.full_name}
          </h3>
        </div>
        <p class="card-desc">${item.description || 'Aucune description disponible.'}</p>
        <div class="card-tags">
          <span class="tag"><i class="fa-solid fa-user"></i> ${item.owner.login}</span>
          ${item.language ? `<span class="tag">${item.language}</span>` : ''}
          <span class="tag"><i class="fa-solid fa-star"></i> ${item.stargazers_count}</span>
          <span class="tag"><i class="fa-solid fa-code-fork"></i> ${item.forks_count}</span>
        </div>
        <div class="card-footer">
          <button class="card-btn" onclick="openGitHubModal('${item.owner.login}', '${item.name}')">
            <i class="fa-solid fa-eye"></i> Aperçu
          </button>
          <a href="${item.html_url}" target="_blank" class="card-btn">
            <i class="fa-brands fa-github"></i> GitHub
          </a>
        </div>
      </div>
    </div>
  `).join('');

  section.innerHTML = `
    <h2 class="category-header-title">${title} (${filtered.length})</h2>
    <div class="${gridClass}">${cardsHtml}</div>
  `;
  container.appendChild(section);
}

function filterCategory(catId) {
  activeMode = 'home';
  activeCategory = catId;
  updateNavState('btn-nav-home');
  renderCategories();
  renderContent();
}

function updateNavState(activeBtnId) {
  document.querySelectorAll('.nav-menu .nav-item').forEach(el => el.classList.remove('active'));
  document.getElementById(activeBtnId)?.classList.add('active');
}

function setupEvents() {
  document.getElementById('search-input')?.addEventListener('input', () => renderContent());
  
  document.getElementById('sort-select')?.addEventListener('change', (e) => {
    currentSort = e.target.value;
    renderContent();
  });

  document.getElementById('btn-nav-home')?.addEventListener('click', (e) => {
    e.preventDefault();
    filterCategory('all');
  });

  document.getElementById('btn-nav-repos')?.addEventListener('click', (e) => {
    e.preventDefault();
    activeMode = 'repos';
    updateNavState('btn-nav-repos');
    renderCategories();
    renderContent();
  });

  document.getElementById('btn-nav-stars')?.addEventListener('click', (e) => {
    e.preventDefault();
    activeMode = 'stars';
    updateNavState('btn-nav-stars');
    renderCategories();
    renderContent();
  });

  document.getElementById('btn-view-grid')?.addEventListener('click', () => {
    isListView = false;
    document.getElementById('btn-view-grid').classList.add('active');
    document.getElementById('btn-view-list').classList.remove('active');
    renderContent();
  });

  document.getElementById('btn-view-list')?.addEventListener('click', () => {
    isListView = true;
    document.getElementById('btn-view-list').classList.add('active');
    document.getElementById('btn-view-grid').classList.remove('active');
    renderContent();
  });

  const modal = document.getElementById('project-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target.id === 'project-modal') closeProjectModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeProjectModal();
  });
}

// Modal pour les projets locaux (JSON)
async function openProjectModal(projectId) {
  const project = globalData.projects.find(p => p.id === projectId);
  if (!project) return;

  const matches = (project.github || '').match(/github\.com\/([^\/]+)\/([^\/]+)/);
  if (matches) {
    const [_, owner, repo] = matches;
    openGitHubModal(owner, repo.replace('.git', ''));
  } else {
    // Mode sans repo GitHub direct
    document.getElementById('modal-title').textContent = project.title;
    document.getElementById('modal-description').textContent = project.description || '';
    document.getElementById('modal-stars').textContent = '-';
    document.getElementById('modal-forks').textContent = '-';
    document.getElementById('modal-release').textContent = '-';
    document.getElementById('modal-readme').innerHTML = '<p>Aucun README GitHub lié.</p>';
    document.getElementById('project-modal').classList.add('active');
  }
}

// Modal unifiée pour afficher l'aperçu complet de tout dépôt GitHub (Repos personnels, Stars, etc.)
async function openGitHubModal(owner, repo) {
  const modal = document.getElementById('project-modal');
  document.getElementById('modal-title').textContent = `${owner}/${repo}`;
  document.getElementById('modal-description').textContent = 'Chargement des détails...';
  document.getElementById('modal-stars').textContent = '...';
  document.getElementById('modal-forks').textContent = '...';
  document.getElementById('modal-release').textContent = '...';
  document.getElementById('modal-readme').innerHTML = '<p>Chargement du README...</p>';
  modal.classList.add('active');

  try {
    const repoRes = await fetch(`https://api.github.com/repos/${owner}/${repo}`);
    if (!repoRes.ok) throw new Error("Dépôt introuvable");
    const repoData = await repoRes.json();

    document.getElementById('modal-title').textContent = repoData.full_name;
    document.getElementById('modal-description').textContent = repoData.description || '';
    document.getElementById('modal-stars').textContent = repoData.stargazers_count;
    document.getElementById('modal-forks').textContent = repoData.forks_count;

    const defaultBranch = repoData.default_branch || 'main';

    // Récupération de la dernière release
    const relRes = await fetch(`https://api.github.com/repos/${owner}/${repo}/releases/latest`);
    if (relRes.ok) {
      const relData = await relRes.json();
      document.getElementById('modal-release').innerHTML = `<span class="release-badge">${relData.tag_name}</span>`;
    } else {
      document.getElementById('modal-release').textContent = 'Aucune release';
    }

    // Récupération du README sur la branche par défaut
    const readmeRes = await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/${defaultBranch}/README.md`);
    
    if (readmeRes.ok) {
      let markdownText = await readmeRes.text();
      const rawBaseUrl = `https://raw.githubusercontent.com/${owner}/${repo}/${defaultBranch}/`;

      // Correction des liens relatifs vers les images (Markdown)
      markdownText = markdownText.replace(/!\[(.*?)\]\((?!http\vert{}https\vert{}\/\/)(.*?)\)/g, (match, alt, path) => {
        const cleanPath = path.startsWith('./') ? path.slice(2) : (path.startsWith('/') ? path.slice(1) : path);
        return `![${alt}](${rawBaseUrl}${cleanPath})`;
      });

      // Correction des images dans les balises HTML <img> (ex: <img src="banner.png">)
      markdownText = markdownText.replace(/<img([^>]+)src=["'](?!http|https|\/\/)([^"']+)["']/g, (match, rest, path) => {
        const cleanPath = path.startsWith('./') ? path.slice(2) : (path.startsWith('/') ? path.slice(1) : path);
        return `<img${rest}src="${rawBaseUrl}${cleanPath}"`;
      });

      document.getElementById('modal-readme').innerHTML = window.marked ? marked.parse(markdownText) : markdownText;
    } else {
      document.getElementById('modal-readme').innerHTML = '<p>Aucun fichier README.md trouvé pour ce dépôt.</p>';
    }

  } catch (err) {
    document.getElementById('modal-readme').innerHTML = `<p>Erreur lors du chargement : ${err.message}</p>`;
  }
}

function closeProjectModal() {
  document.getElementById('project-modal').classList.remove('active');
}