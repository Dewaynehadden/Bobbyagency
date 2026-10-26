'use strict';

const { services, projects } = window.BOBBY_DATA;
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const iconMarkup = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;

// Navigation: native anchors still work when JavaScript is unavailable.
const menuToggle = $('.menu-toggle');
const navigation = $('#main-navigation');
function closeNavigation() {
  navigation.classList.remove('open');
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', 'Open navigation');
}
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  navigation.classList.toggle('open', open);
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
navigation.addEventListener('click', event => {
  if (event.target.closest('a, [data-enquire], [data-quote]')) closeNavigation();
});
document.addEventListener('click', event => {
  if (!navigation.contains(event.target) && !menuToggle.contains(event.target)) closeNavigation();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
    closeNavigation();
    menuToggle.focus();
  }
});
window.addEventListener('resize', () => {
  if (window.innerWidth > 1050) closeNavigation();
});
const navObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    $$('#main-navigation > a').forEach(link => {
      const active = link.getAttribute('href') === `#${entry.target.id}`;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  });
}, { rootMargin: '-15% 0px -60% 0px', threshold: 0 });
$$('main > section[id]').forEach(section => navObserver.observe(section));
$('#year').textContent = String(new Date().getFullYear());

// Carousel: stop while someone is reading or using a banner's controls.
const carousel = $('.hero-carousel');
const slides = $$('.hero-slide');
const slideDots = $$('[data-goto]');
const pauseButton = $('.carousel-pause');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let currentSlide = 0;
let manuallyPaused = reducedMotion.matches;
let carouselTimer;
function showSlide(index) {
  currentSlide = (index + slides.length) % slides.length;
  slides.forEach((slide, i) => { slide.hidden = i !== currentSlide; });
  slideDots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === currentSlide)));
}
function updatePauseControl() {
  pauseButton.setAttribute('aria-label', manuallyPaused ? 'Resume banner rotation' : 'Pause banner rotation');
  pauseButton.setAttribute('aria-pressed', String(manuallyPaused));
  pauseButton.innerHTML = iconMarkup(manuallyPaused ? 'play' : 'pause');
}
function stopCarousel() { window.clearInterval(carouselTimer); }
function startCarousel() {
  stopCarousel();
  if (manuallyPaused || document.hidden || carousel.matches(':hover') || carousel.contains(document.activeElement)) return;
  carouselTimer = window.setInterval(() => showSlide(currentSlide + 1), 6000);
}
$$('[data-carousel]').forEach(button => button.addEventListener('click', () => {
  showSlide(currentSlide + (button.dataset.carousel === 'next' ? 1 : -1));
  startCarousel();
}));
slideDots.forEach(dot => dot.addEventListener('click', () => {
  showSlide(Number(dot.dataset.goto));
  startCarousel();
}));
pauseButton.addEventListener('click', () => {
  manuallyPaused = !manuallyPaused;
  updatePauseControl();
  startCarousel();
});
carousel.addEventListener('mouseenter', stopCarousel);
carousel.addEventListener('mouseleave', startCarousel);
carousel.addEventListener('focusin', stopCarousel);
carousel.addEventListener('focusout', () => window.setTimeout(startCarousel, 0));
document.addEventListener('visibilitychange', startCarousel);
reducedMotion.addEventListener('change', event => {
  if (event.matches) manuallyPaused = true;
  updatePauseControl();
  startCarousel();
});
updatePauseControl();
startCarousel();

// Dialogs use the browser's focus trap, Escape handling, and focus restoration.
function openDialog(dialog) {
  $$('dialog[open]').forEach(open => open.close());
  dialog.showModal();
  document.body.classList.add('modal-open');
}
$$('dialog').forEach(dialog => {
  $('[data-close]', dialog).addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const controls = $$('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])', dialog)
      .filter(element => element.getClientRects().length && !element.closest('[hidden]'));
    const first = controls[0];
    const last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  });
  dialog.addEventListener('close', () => {
    if (!$('dialog[open]')) document.body.classList.remove('modal-open');
    $$('video', dialog).forEach(video => video.pause());
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
});
let selectedServiceIndex = 0;
function showService(index) {
  const service = services[index];
  if (!service) return;
  selectedServiceIndex = index;
  $('#service-title').textContent = service.title;
  $('#service-category').textContent = service.category.toUpperCase();
  $('#service-description').textContent = service.desc;
  const serviceImage = $('#service-dialog-image');
  serviceImage.src = service.image;
  serviceImage.className = 'service-real-photo';
  serviceImage.style.removeProperty('--photo-col');
  serviceImage.style.removeProperty('--photo-row');
  serviceImage.alt = service.imageAlt;
  $('#service-dialog-package').replaceChildren();
  for (const text of [`Est. ${service.deliveryDays} days`, `Up to ${service.revisions} revisions`]) {
    const item = document.createElement('span');
    item.textContent = text;
    $('#service-dialog-package').append(item);
  }
  const includes = $('#service-includes');
  includes.replaceChildren();
  service.includes.forEach(text => {
    const item = document.createElement('li');
    item.innerHTML = iconMarkup('check');
    item.append(document.createTextNode(text));
    includes.append(item);
  });
  openDialog($('#service-dialog'));
}
function openEnquiry(service = 'New website project', website = '') {
  const select = $('#client-service');
  if (![...select.options].some(option => option.value === service)) service = 'New website project';
  select.value = service;
  // Keep an in-progress brief when opening a different service.
  if (website) {
    $('#client-site').value = website;
    if (!$('#client-message').value.trim()) $('#client-message').value = 'I would like a personal review of my public storefront, including design, navigation, product pages, and the mobile experience.';
  }
  $('#enquiry-status').textContent = 'Your email app opens with your brief. Please send it there — nothing is sent or stored automatically.';
  $('#email-fallback').hidden = true;
  openDialog($('#enquiry-dialog'));
}
document.addEventListener('click', event => {
  const serviceButton = event.target.closest('[data-service]');
  if (serviceButton) showService(Number(serviceButton.dataset.service));
  const quoteButton = event.target.closest('[data-quote]');
  if (quoteButton) openQuote(quoteButton.dataset.quote === 'general' ? null : Number(quoteButton.dataset.quote));
  const enquireButton = event.target.closest('[data-enquire]');
  if (enquireButton) openEnquiry(enquireButton.dataset.enquire);
});
$('#service-modal-quote').addEventListener('click', () => openQuote(selectedServiceIndex));
let quoteServiceIndex = 0;
function openQuote(index) {
  if (index !== null && !services[index]) return;
  quoteServiceIndex = index;
  $('#quote-service-name').textContent = services[index]?.title || 'New website project';
  openDialog($('#quote-dialog'));
}
$('#quote-email-option').addEventListener('click', () => openEnquiry(services[quoteServiceIndex]?.title || 'New website project'));
$('#meet-founder').addEventListener('click', () => openDialog($('#founder-dialog')));

// Public URL validation only. No request is made to the submitted store.
function normalizeWebsite(value) {
  const input = value.trim();
  if (!input) return null;
  try {
    const url = new URL(/^[a-z][a-z\d+.-]*:/i.test(input) ? input : `https://${input}`);
    if (!['https:', 'http:'].includes(url.protocol) || !url.hostname.includes('.') || url.username || url.password || /\s/.test(input)) return null;
    return url.href;
  } catch { return null; }
}
$('#audit-form').addEventListener('submit', event => {
  event.preventDefault();
  const input = $('#store-url');
  const website = normalizeWebsite(input.value);
  if (!website) {
    $('#audit-error').textContent = 'Please enter a public website address, such as yourstore.com or https://yourstore.com.';
    input.setAttribute('aria-invalid', 'true');
    input.focus();
    return;
  }
  $('#audit-error').textContent = '';
  input.removeAttribute('aria-invalid');
  openEnquiry('Free store review', website);
});
$('#store-url').addEventListener('input', () => {
  $('#store-url').removeAttribute('aria-invalid');
  $('#audit-error').textContent = '';
});
$('#client-site').addEventListener('input', event => event.target.setCustomValidity(''));
$('#enquiry-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  const websiteInput = $('#client-site');
  const rawWebsite = websiteInput.value.trim();
  const website = rawWebsite ? normalizeWebsite(rawWebsite) : '';
  if (rawWebsite && !website) {
    websiteInput.setCustomValidity('Enter a website address such as yourstore.com, or leave this field empty.');
    websiteInput.reportValidity();
    return;
  }
  websiteInput.setCustomValidity('');
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  const name = String(data.get('client-name')).trim();
  const message = String(data.get('client-message')).trim();
  if (!name || !message) {
    $('#enquiry-status').textContent = 'Please add your name and a short description of your project.';
    return;
  }
  const service = String(data.get('client-service'));
  const subject = `Bobbyagency enquiry: ${service}`;
  const body = `Hi Timmy,\n\nMy name is ${name}.\nEmail: ${data.get('client-email')}\nService: ${service}\n${website ? `Website: ${website}\n` : ''}\n${message}\n\nLooking forward to hearing from you.`;
  const href = `mailto:dewaynehadden11@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  const fallback = $('#email-fallback');
  fallback.href = href;
  fallback.hidden = false;
  $('#enquiry-status').textContent = 'Your email brief is ready. Please send it in your email app. If no app opens, use the prepared email link below, email us directly, or message on WhatsApp. Your message has not been sent by this website.';
  window.open(href, '_blank', 'noopener,noreferrer');
});

// Portfolio filters, search, and pagination operate on the same dataset.
let activeFilter = 'All';
let visibleProjectCount = 4;
const searchInput = $('#project-search');
function projectElement(project) {
  const card = document.createElement('a');
  card.className = 'project-card';
  card.href = project.url;
  card.target = '_blank';
  card.rel = 'noopener';
  const cover = document.createElement('div');
  cover.className = 'project-cover';
  if (project.image) {
    const image = document.createElement('img');
    image.src = `assets/${project.image}`;
    image.alt = `${project.title} preview`;
    image.width = 1280;
    image.height = 900;
    image.loading = 'lazy';
    cover.append(image);
  } else {
    const art = document.createElement('div');
    art.className = 'portfolio-art';
    art.style.setProperty('--art-accent', project.accent);
    const kicker = document.createElement('small');
    kicker.textContent = 'THE BOBBYAGENCY';
    const title = document.createElement('b');
    title.textContent = project.art;
    const footer = document.createElement('span');
    footer.textContent = 'PORTFOLIO COLLECTION';
    art.append(kicker, title, footer);
    cover.append(art);
  }
  const kind = document.createElement('span');
  kind.className = 'project-kind';
  kind.textContent = project.type;
  const arrow = document.createElement('span');
  arrow.className = 'project-open';
  arrow.innerHTML = iconMarkup('arrow-up');
  cover.append(kind, arrow);
  const copy = document.createElement('div');
  copy.className = 'project-copy';
  const title = document.createElement('h3');
  title.textContent = project.title;
  const description = document.createElement('p');
  description.textContent = project.desc;
  const meta = document.createElement('div');
  meta.className = 'project-meta';
  const destination = document.createElement('span');
  destination.textContent = project.image ? 'Explore live demo ↗' : 'View on Upwork ↗';
  const category = document.createElement('span');
  category.textContent = project.category;
  meta.append(destination, category);
  copy.append(title, description, meta);
  card.append(cover, copy);
  return card;
}
function renderProjects() {
  const search = searchInput.value.trim().toLowerCase();
  const filtered = projects.filter(project => {
    const matchesCategory = activeFilter === 'All' || project.tags.includes(activeFilter);
    const matchesSearch = `${project.title} ${project.category} ${project.desc} ${project.type}`.toLowerCase().includes(search);
    return matchesCategory && matchesSearch;
  });
  const visible = filtered.slice(0, visibleProjectCount);
  $('#project-grid').replaceChildren(...visible.map(projectElement));
  $('#project-empty').hidden = filtered.length !== 0;
  const remaining = filtered.length - visible.length;
  $('#load-more').hidden = remaining <= 0;
  $('#load-more').innerHTML = `Show more projects (${remaining}) ${iconMarkup('down')}`;
  $('#project-count').textContent = `Showing ${visible.length} of ${filtered.length} ${filtered.length === 1 ? 'project' : 'projects'}${activeFilter !== 'All' ? ` · ${activeFilter}` : ''}`;
  $$('[data-filter]').forEach(button => {
    const active = button.dataset.filter === activeFilter;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
}
$$('[data-filter]').forEach(button => button.addEventListener('click', () => {
  activeFilter = button.dataset.filter;
  visibleProjectCount = 4;
  renderProjects();
}));
searchInput.addEventListener('input', () => {
  visibleProjectCount = 4;
  renderProjects();
});
$('#load-more').addEventListener('click', () => {
  const oldCount = $$('#project-grid .project-card').length;
  visibleProjectCount += 4;
  renderProjects();
  const firstNewCard = $$('#project-grid .project-card')[oldCount];
  if (firstNewCard) firstNewCard.focus({ preventScroll: true });
});
$('#reset-projects').addEventListener('click', () => {
  activeFilter = 'All';
  searchInput.value = '';
  visibleProjectCount = 4;
  renderProjects();
  searchInput.focus();
});
renderProjects();

// Project walkthrough tabs also support the expected keyboard controls.
const showcaseTabs = $$('[data-showcase]');
function selectShowcase(tab, focus = false) {
  showcaseTabs.forEach(button => {
    const selected = button === tab;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
    $(`#panel-${button.dataset.showcase}`).hidden = !selected;
  });
  if (focus) tab.focus();
}
showcaseTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectShowcase(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % showcaseTabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + showcaseTabs.length) % showcaseTabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = showcaseTabs.length - 1;
    if (next !== undefined) {
      event.preventDefault();
      selectShowcase(showcaseTabs[next], true);
    }
  });
});

// Factual information about this static site and the project enquiry process.
const information = {
  privacy: {
    title: 'Privacy information',
    content: '<p>This website is a static portfolio. Its project and store-review forms prepare an email in your own email application. The website does not send, store, or upload the details you enter, and it does not request store passwords or admin access.</p><h3>Third-party services</h3><p>WhatsApp, Upwork, Fiverr, LinkedIn, Telegram, and email providers have their own privacy practices. Their websites open only when you choose a corresponding link. The testimonial video and images are served from this website.</p><h3>Hosting and enquiries</h3><p>For our service privacy policy, see <a href="terms.html#privacy">Terms &amp; Refund Policy</a>. Your hosting provider may keep standard request logs. Details you send by email or chat are handled through the service you choose. Contact <a href="mailto:dewaynehadden11@gmail.com">dewaynehadden11@gmail.com</a> with privacy questions about an enquiry.</p>'
  }
};
$$('[data-legal]').forEach(button => button.addEventListener('click', () => {
  const item = information[button.dataset.legal];
  if (!item) return;
  $('#information-title').textContent = item.title;
  $('#information-content').innerHTML = item.content;
  openDialog($('#information-dialog'));
}));

// Dashboard reports and testimonials share a single active video player.
const portfolioVideos = $$('main video');
portfolioVideos.forEach(video => video.addEventListener('play', () => {
  portfolioVideos.forEach(other => { if (other !== video) other.pause(); });
}));
const reportVisibility = new IntersectionObserver(entries => {
  entries.forEach(entry => { if (!entry.isIntersecting) entry.target.pause(); });
}, { threshold: 0.1 });
portfolioVideos.forEach(video => reportVisibility.observe(video));

// Wheel rotation can be paused independently and honors reduced motion.
const expertiseWheel = $('.expertise-orbit');
const orbitToggle = $('.orbit-toggle');
if (expertiseWheel && orbitToggle) {
  let wheelPaused = reducedMotion.matches;
  function updateWheel() {
    expertiseWheel.classList.toggle('is-paused', wheelPaused);
    orbitToggle.setAttribute('aria-pressed', String(wheelPaused));
    orbitToggle.setAttribute('aria-label', wheelPaused ? 'Resume wheel rotation' : 'Pause wheel rotation');
    orbitToggle.textContent = wheelPaused ? 'Resume rotation' : 'Pause rotation';
    orbitToggle.disabled = reducedMotion.matches;
    if (reducedMotion.matches) {
      orbitToggle.textContent = 'Rotation off · reduced motion';
      orbitToggle.setAttribute('aria-label', 'Wheel rotation is off for reduced motion');
    }
  }
  orbitToggle.addEventListener('click', () => { wheelPaused = !wheelPaused; updateWheel(); });
  reducedMotion.addEventListener('change', event => { wheelPaused = event.matches; updateWheel(); });
  updateWheel();
}

// Shared manual carousels for client recommendations and sales reports.
$$('[data-video-carousel]').forEach(carousel => {
  const track = $('.media-track', carousel);
  const cards = $$(':scope > article', track);
  const previous = $('.media-prev', carousel);
  const next = $('.media-next', carousel);
  const dots = $('.media-dots', carousel);
  const position = $('.media-position', carousel);
  let starts = [];
  let currentPage = 0;
  let visibleCount = 0;
  function update() {
    const step = cards.length > 1 ? cards[1].offsetLeft - cards[0].offsetLeft : cards[0].offsetWidth;
    const first = Math.max(0, Math.min(cards.length - visibleCount, Math.round(track.scrollLeft / step)));
    currentPage = starts.reduce((closest, start, index) => Math.abs(start - first) < Math.abs(starts[closest] - first) ? index : closest, 0);
    previous.disabled = currentPage === 0;
    next.disabled = currentPage === starts.length - 1;
    position.textContent = `${first + 1}–${Math.min(cards.length, first + visibleCount)} of ${cards.length} videos`;
    $$('button', dots).forEach((dot, index) => dot.setAttribute('aria-current', String(index === currentPage)));
  }
  function goTo(pageIndex) {
    const first = starts[Math.max(0, Math.min(starts.length - 1, pageIndex))];
    track.scrollTo({ left: cards[first].offsetLeft - cards[0].offsetLeft, behavior: reducedMotion.matches ? 'instant' : 'smooth' });
  }
  function layout() {
    const newCount = window.matchMedia('(max-width: 600px)').matches ? 1 : 2;
    if (newCount !== visibleCount) {
      visibleCount = newCount;
      starts = [...new Set(Array.from({ length: Math.ceil(cards.length / visibleCount) }, (_, i) => Math.min(cards.length - visibleCount, i * visibleCount)))];
      dots.replaceChildren(...starts.map((first, index) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.setAttribute('aria-label', `Show videos ${first + 1}${visibleCount > 1 ? `–${Math.min(cards.length, first + visibleCount)}` : ''}`);
        dot.addEventListener('click', () => goTo(index));
        return dot;
      }));
    }
    update();
  }
  previous.addEventListener('click', () => goTo(currentPage - 1));
  next.addEventListener('click', () => goTo(currentPage + 1));
  track.addEventListener('scroll', update, { passive: true });
  track.addEventListener('keydown', event => {
    if (event.target !== track) return;
    const actions = { ArrowLeft: currentPage - 1, ArrowRight: currentPage + 1, Home: 0, End: starts.length - 1 };
    if (event.key in actions) { event.preventDefault(); goTo(actions[event.key]); }
  });
  new ResizeObserver(layout).observe(track);
  layout();
});

// Progressive service finder: all cards remain available without JavaScript.
const serviceFinder = $('.service-finder');
if (serviceFinder) {
  const cards = $$('.service-card');
  const search = $('#service-search');
  const showAllButton = $('#service-show-all');
  let selectedGroup = 'All services';
  let showAll = false;
  function renderServices() {
    const query = search.value.trim().toLowerCase();
    const matches = cards.map((card, index) => ({ card, service: services[index] }))
      .filter(({ service }) => (selectedGroup === 'All services' || service.group === selectedGroup)
        && `${service.title} ${service.desc} ${service.category}`.toLowerCase().includes(query));
    const visible = new Set((showAll ? matches : matches.slice(0, 9)).map(item => item.card));
    cards.forEach(card => { card.hidden = !visible.has(card); });
    $('#service-results-count').textContent = `Showing ${visible.size} of ${matches.length} services`;
    $('.service-empty').hidden = matches.length !== 0;
    showAllButton.hidden = matches.length <= 9;
    showAllButton.textContent = showAll ? 'Show fewer services' : `View all ${matches.length} services`;
    showAllButton.setAttribute('aria-expanded', String(showAll));
    $$('[data-service-filter]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.serviceFilter === selectedGroup)));
  }
  serviceFinder.hidden = false;
  $('.service-explore').hidden = false;
  $$('[data-service-filter]').forEach(button => button.addEventListener('click', () => {
    selectedGroup = button.dataset.serviceFilter;
    showAll = false;
    renderServices();
  }));
  search.addEventListener('input', () => { showAll = false; renderServices(); });
  showAllButton.addEventListener('click', () => {
    showAll = !showAll;
    renderServices();
    if (!showAll) $('#services .service-finder').scrollIntoView({ behavior: reducedMotion.matches ? 'instant' : 'smooth', block: 'start' });
  });
  $('#reset-services').addEventListener('click', () => {
    search.value = '';
    selectedGroup = 'All services';
    showAll = false;
    renderServices();
    search.focus();
  });
  renderServices();
}

// Display business totals only when supplied; otherwise use factual portfolio context.
const businessMetrics = window.BOBBY_DATA.businessMetrics || {};
const metricDetails = {
  totalProjects: ['Total projects', 'Across previous client engagements'],
  countriesServed: ['Countries served', 'Client locations served'],
  successRate: [businessMetrics.successRateLabel || 'Success rate', businessMetrics.successBasis || 'Reported project outcomes']
};
Object.entries(metricDetails).forEach(([key, [label, note]]) => {
  const value = businessMetrics[key];
  const card = $(`[data-business-metric="${key}"]`);
  if (!card) return;
  if (value === null || value === undefined || !Number.isFinite(Number(value)) || Number(value) < 0) return;
  if (key === 'successRate' && Number(value) > 100) return;
  $('[data-metric-value]', card).textContent = `${Number(value).toLocaleString('en-US')}${key === 'successRate' ? '%' : key === 'totalProjects' && businessMetrics.totalProjectsAtLeast ? '+' : ''}`;
  $('[data-metric-label]', card).textContent = label;
  $('[data-metric-note]', card).textContent = note;
});

// Staggered reveals and counters run once in view, and never hide reduced-motion content.
const revealCards = $$('.trust-card, .portfolio-stat-card, .service-card, .project-process-grid article');
let cardRevealObserver;
function initializeCardMotion() {
  cardRevealObserver?.disconnect();
  revealCards.forEach((card, index) => {
    card.style.setProperty('--reveal-delay', `${(index % 3) * 85}ms`);
    card.classList.add('motion-reveal');
    if (reducedMotion.matches) {
      card.classList.remove('reveal-ready');
      card.classList.add('is-revealed');
    }
  });
  if (reducedMotion.matches) return;
  cardRevealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-revealed');
      cardRevealObserver.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  revealCards.forEach(card => {
    if (!card.classList.contains('is-revealed')) {
      card.classList.add('reveal-ready');
      cardRevealObserver.observe(card);
    }
  });
}
initializeCardMotion();
reducedMotion.addEventListener('change', initializeCardMotion);

const countCards = $$('[data-business-metric]').filter(card => {
  const value = businessMetrics[card.dataset.businessMetric];
  return value !== null && value !== undefined && Number.isFinite(Number(value));
});
const counterFrames = new Map();
function counterText(card, value) {
  const key = card.dataset.businessMetric;
  return `${value.toLocaleString('en-US')}${key === 'successRate' ? '%' : key === 'totalProjects' && businessMetrics.totalProjectsAtLeast ? '+' : ''}`;
}
function finishCounter(card) {
  if (counterFrames.has(card)) cancelAnimationFrame(counterFrames.get(card));
  counterFrames.delete(card);
  $('[data-metric-value]', card).textContent = counterText(card, Number(businessMetrics[card.dataset.businessMetric]));
  card.dataset.counted = 'true';
}
function animateCounter(card) {
  if (card.dataset.counted === 'true' || reducedMotion.matches) { finishCounter(card); return; }
  card.dataset.counted = 'true';
  const target = Number(businessMetrics[card.dataset.businessMetric]);
  const output = $('[data-metric-value]', card);
  output.setAttribute('aria-label', counterText(card, target));
  const began = performance.now();
  function frame(now) {
    const progress = Math.min(1, (now - began) / 1500);
    const eased = 1 - Math.pow(1 - progress, 3);
    output.textContent = counterText(card, Math.round(target * eased));
    if (progress < 1 && !reducedMotion.matches) counterFrames.set(card, requestAnimationFrame(frame));
    else finishCounter(card);
  }
  counterFrames.set(card, requestAnimationFrame(frame));
}
const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      counterObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.55 });
countCards.forEach(card => reducedMotion.matches ? finishCounter(card) : counterObserver.observe(card));
reducedMotion.addEventListener('change', event => {
  if (event.matches) {
    counterObserver.disconnect();
    countCards.forEach(finishCounter);
  }
});
